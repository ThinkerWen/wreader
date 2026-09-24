import { useEffect, useRef, useState } from 'react'
import { Button, Input, Spinner, TextField } from '@heroui/react'
import { ArrowLeft, ArrowRight, BookMarked, BookOpen, Bookmark, Check, ChevronLeft, ChevronRight, Compass, LibraryBig, List, Menu, Minus, Moon, Plus, Search, Settings2, Sun, Trash2, X } from 'lucide-react'
import { addToLibrary, bookKey, getChapters, getContent, getLibrary, legacyData, login, putProgress, removeFromLibrary, searchBooks, setToken, toProgress } from './library'
import type { Chapter, Novel, ProgressMap, ServerBook } from './library'

type View = 'shelf' | 'discover' | 'detail' | 'reader'
type Theme = 'paper' | 'night'
const covers = ['cover-olive', 'cover-rust', 'cover-slate', 'cover-moss', 'cover-ink', 'cover-clay']
function coverTone(book: Novel) { return covers[[...book.name].reduce((n, c) => n + c.charCodeAt(0), 0) % covers.length] }
function Cover({ book, large = false }: { book: Novel; large?: boolean }) {
  const [failed, setFailed] = useState(false)
  return <div className={`book-cover ${coverTone(book)} ${large ? 'book-cover-large' : ''}`}>
    {book.cover_url && !failed ? <img src={book.cover_url} alt={`${book.name}封面`} onError={() => setFailed(true)} /> : <><span className="cover-decoration">✳</span><span className="cover-title">{book.name}</span><span className="cover-author">{book.author || '佚名'}</span><span className="cover-bottom">W · READER</span></>}
  </div>
}
function ErrorNotice({ message, retry }: { message: string; retry?: () => void }) {
  return <div className="notice" role="alert"><span>{message}</span>{retry && <Button size="sm" variant="outline" onPress={retry}>重试</Button>}</div>
}
function App() {
  const [view, setView] = useState<View>('shelf')
  const [books, setBooks] = useState<ServerBook[]>([])
  const [progress, setProgress] = useState<ProgressMap>({})
  const [session, setSession] = useState(false)
  const [password, setPassword] = useState('')
  const [authError, setAuthError] = useState('')
  const [libraryError, setLibraryError] = useState('')
  const [busy, setBusy] = useState(false)
  const [syncError, setSyncError] = useState('')
  const [pendingProgress, setPendingProgress] = useState<{ id: number; chapter: Chapter; index: number } | null>(null)
  const [importMessage, setImportMessage] = useState('')
  const [importing, setImporting] = useState(false)
  const [legacy, setLegacy] = useState<ReturnType<typeof legacyData>>(null)
  const [query, setQuery] = useState('')
  const [searched, setSearched] = useState('')
  const [results, setResults] = useState<Novel[]>([])
  const [selected, setSelected] = useState<Novel | null>(null)
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [chapterIndex, setChapterIndex] = useState(0)
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [catalogLoading, setCatalogLoading] = useState(false)
  const [readingLoading, setReadingLoading] = useState(false)
  const [error, setError] = useState('')
  const [catalogError, setCatalogError] = useState('')
  const [readingError, setReadingError] = useState('')
  const [theme, setTheme] = useState<Theme>(() => localStorage.getItem('wreader-theme') === 'night' ? 'night' : 'paper')
  const [fontSize, setFontSize] = useState(() => Number(localStorage.getItem('wreader-font')) || 19)
  const [showCatalog, setShowCatalog] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [mobileNav, setMobileNav] = useState(false)
  const requestId = useRef(0)
  const scrollRef = useRef<HTMLElement>(null)

  useEffect(() => {
    const unauthorized = () => { setSession(false); setToken(null); setBooks([]); setProgress({}); setAuthError('登录已失效，请重新登录') }
    window.addEventListener('wreader-unauthorized', unauthorized)
    return () => window.removeEventListener('wreader-unauthorized', unauthorized)
  }, [])
  function applyLibrary(items: ServerBook[]) {
    setBooks(items)
    setProgress(Object.fromEntries(items.filter(b => b.progress).map(b => [bookKey(b), toProgress(b.progress!)])))
  }
  async function reloadLibrary() {
    setLibraryError('')
    try { applyLibrary((await getLibrary()).books) }
    catch (e) { setLibraryError(e instanceof Error ? e.message : '书架加载失败') }
  }
  async function signIn(e: React.FormEvent) {
    e.preventDefault(); setBusy(true); setAuthError('')
    try {
      await login(password)
      const result = await getLibrary()
      applyLibrary(result.books); setSession(true); setPassword('')
      try { setLegacy(legacyData()) } catch (error) { setImportMessage(error instanceof Error ? error.message : '旧数据读取失败') }
    } catch (error) { setAuthError(error instanceof Error ? error.message : '登录失败'); setToken(null) }
    finally { setBusy(false) }
  }
  async function importLegacy() {
    if (!legacy || importing) return
    setImporting(true)
    let imported = 0, skipped = legacy.skipped, failed = 0
    const errors: string[] = []
    const seen = new Set<string>()
    try {
      for (const book of legacy.books) {
        const key = bookKey(book)
        if (seen.has(key)) { skipped++; continue }
        seen.add(key)
        try {
          const stored = await addToLibrary(book)
          const item = legacy.progress[key]
          if (item !== undefined) {
            if (item && typeof item.chapterUrl === 'string' && item.chapterUrl.length > 0 && item.chapterUrl.length <= 2048 && typeof item.chapterName === 'string' && item.chapterName.length > 0 && item.chapterName.length <= 256 && Number.isInteger(item.index) && item.index >= 0 && item.index <= 1000000 && Number.isInteger(item.updatedAt) && item.updatedAt >= 946684800000 && item.updatedAt <= Date.now() + 300000) {
              const saved = await putProgress(stored.book_id, { url: item.chapterUrl, name: item.chapterName }, item.index, item.updatedAt)
              if (saved.updated_at !== item.updatedAt) skipped++
            } else skipped++
          }
          imported++
        } catch (error) { failed++; errors.push(`${book.name}: ${error instanceof Error ? error.message : '导入失败'}`) }
      }
      try { applyLibrary((await getLibrary()).books); setLibraryError('') }
      catch (error) { failed++; setLibraryError(error instanceof Error ? error.message : '书架加载失败'); errors.push('书架刷新失败') }
      setImportMessage(`成功 ${imported} 本，跳过 ${skipped} 项，失败 ${failed} 项。${errors.slice(0, 3).join('；')}${failed ? '；可重试，旧数据未删除。' : '旧数据已保留。'}`)
    } finally { setImporting(false) }
  }
  useEffect(() => { localStorage.setItem('wreader-theme', theme) }, [theme])
  useEffect(() => { localStorage.setItem('wreader-font', String(fontSize)) }, [fontSize])

  async function search(keyword = query) {
    const value = keyword.trim()
    if (!value) return
    requestId.current++
    const id = requestId.current
    setQuery(value); setSearched(value); setResults([]); setError(''); setLoading(true); setView('discover')
    try { const data = await searchBooks(value); if (id === requestId.current) setResults(data) }
    catch (e) { if (id === requestId.current) setError(e instanceof Error ? e.message : '搜索失败，请稍后重试') }
    finally { if (id === requestId.current) setLoading(false) }
  }
  function navigate(next: View) {
    requestId.current++
    setMobileNav(false); setShowCatalog(false); setView(next)
  }
  async function openBook(book: Novel) {
    requestId.current++
    const id = requestId.current
    setSelected(book); setChapters([]); setCatalogError(''); setCatalogLoading(true); setView('detail')
    try { const data = await getChapters(book); if (id === requestId.current) setChapters(data) }
    catch (e) { if (id === requestId.current) setCatalogError(e instanceof Error ? e.message : '目录加载失败') }
    finally { if (id === requestId.current) setCatalogLoading(false) }
  }
  async function readChapter(index: number, list = chapters, book = selected) {
    if (!book || !list[index]) return
    requestId.current++
    const id = requestId.current
    setSelected(book); setChapterIndex(index); setReadingError(''); setContent(''); setReadingLoading(true); setView('reader'); setShowCatalog(false)
    scrollRef.current?.scrollTo(0, 0)
    try {
      const text = await getContent(book, list[index])
      if (id !== requestId.current) return
      setContent(text); setSyncError(''); setPendingProgress(null)
      const stored = books.find(b => bookKey(b) === bookKey(book))
      if (stored) {
        try { const saved = await putProgress(stored.book_id, list[index], index); if (id === requestId.current) { setProgress(prev => ({ ...prev, [bookKey(book)]: toProgress(saved) })); setSyncError('') } }
        catch (error) { if (id === requestId.current) { setPendingProgress({ id: stored.book_id, chapter: list[index], index }); setSyncError(`进度未同步：${error instanceof Error ? error.message : '请求失败'}`) } }
      }
    } catch (e) { if (id === requestId.current) setReadingError(e instanceof Error ? e.message : '正文加载失败') }
    finally { if (id === requestId.current) setReadingLoading(false) }
  }
  async function retryProgress() {
    if (!pendingProgress || !selected) return
    const { id, chapter, index } = pendingProgress
    const currentRequest = requestId.current
    const key = bookKey(selected)
    try { const saved = await putProgress(id, chapter, index); if (currentRequest === requestId.current) { setProgress(prev => ({ ...prev, [key]: toProgress(saved) })); setSyncError(''); setPendingProgress(null) } }
    catch (error) { if (currentRequest === requestId.current) setSyncError(`进度未同步：${error instanceof Error ? error.message : '请求失败'}`) }
  }
  function resume(book: Novel) {
    const saved = progress[bookKey(book)]
    const found = chapters.findIndex(c => c.url === saved?.chapterUrl)
    void readChapter(found >= 0 ? found : saved && saved.index < chapters.length ? saved.index : 0)
  }
  async function addBook(book: Novel) {
    if (busy) return
    setBusy(true); setLibraryError('')
    try { const stored = await addToLibrary(book); setBooks(prev => prev.some(b => b.book_id === stored.book_id) ? prev : [stored, ...prev]) }
    catch (e) { setLibraryError(e instanceof Error ? e.message : '添加书籍失败') }
    finally { setBusy(false) }
  }
  async function removeBook(book: Novel) {
    if (busy) return
    const stored = books.find(b => bookKey(b) === bookKey(book))
    if (!stored) return
    setBusy(true); setLibraryError('')
    try { await removeFromLibrary(stored.book_id); setBooks(prev => prev.filter(b => b.book_id !== stored.book_id)); setProgress(prev => { const next = { ...prev }; delete next[bookKey(book)]; return next }) }
    catch (e) { setLibraryError(e instanceof Error ? e.message : '移除书籍失败') }
    finally { setBusy(false) }
  }
  const saved = selected && books.some(b => bookKey(b) === bookKey(selected))
  const recent = [...books].sort((a, b) => (progress[bookKey(b)]?.updatedAt || 0) - (progress[bookKey(a)]?.updatedAt || 0))[0]
  const current = chapters[chapterIndex]

  if (!session) return <main className="app-shell"><div className="page-content" style={{ maxWidth: 460, margin: '12vh auto' }}><h1>登录拾页</h1><p>登录后从服务端读取书架与进度。</p><form onSubmit={e => void signIn(e)}><label htmlFor="password">密码</label><input id="password" type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} required /><Button type="submit" variant="primary" isDisabled={busy}>登录</Button></form>{authError && <ErrorNotice message={authError} />}</div></main>
  return <div className={`app-shell ${view === 'reader' ? `reading-shell theme-${theme}` : ''}`}>
    {view !== 'reader' && <aside className={`sidebar ${mobileNav ? 'sidebar-open' : ''}`}>
      <div className="brand" onClick={() => navigate('shelf')} role="button" tabIndex={0} onKeyDown={e => { if (e.key === 'Enter') navigate('shelf') }}><div className="brand-icon"><BookOpen size={22} strokeWidth={1.7} /></div><div><strong>拾页</strong><small>W · READER</small></div></div>
      <div className="sidebar-label">你的阅读空间</div>
      <nav aria-label="主导航"><button className={`nav-item ${view === 'shelf' ? 'active' : ''}`} onClick={() => navigate('shelf')}><LibraryBig size={19} /> 我的书架 <span>{books.length || ''}</span></button><button className={`nav-item ${view === 'discover' ? 'active' : ''}`} onClick={() => navigate('discover')}><Compass size={19} /> 发现好书</button></nav>
      <div className="sidebar-spacer" />
      <div className="sidebar-quote"><span>“</span><p>读一本书，<br />遇见另一种生活。</p><div className="quote-rule" /> <small>让故事在此刻发生</small></div>
      <div className="sidebar-footer"><span className="status-dot" /> 书架与进度保存在服务端</div>
    </aside>}
    {mobileNav && <button className="nav-backdrop" aria-label="关闭菜单" onClick={() => setMobileNav(false)} />}
    {view === 'reader' ? <main className="reader-view" ref={scrollRef}>
      <header className="reader-toolbar"><Button variant="ghost" onPress={() => navigate('detail')}><ArrowLeft size={18} /> 返回书籍</Button><span className="reader-book-name">{selected?.name}</span><div className="toolbar-actions"><Button isIconOnly variant="ghost" aria-label="目录" onPress={() => { setShowCatalog(!showCatalog); setShowSettings(false) }}><List size={19} /></Button><Button isIconOnly variant="ghost" aria-label="阅读设置" onPress={() => { setShowSettings(!showSettings); setShowCatalog(false) }}><Settings2 size={19} /></Button></div></header>
      {showCatalog && <div className="reader-panel catalog-panel"><div className="panel-heading"><strong>章节目录</strong><Button isIconOnly variant="ghost" aria-label="关闭目录" onPress={() => setShowCatalog(false)}><X size={18} /></Button></div><div className="panel-scroll">{chapters.map((c, i) => <button key={c.url} className={`panel-chapter ${i === chapterIndex ? 'current' : ''}`} onClick={() => void readChapter(i)}><span>{String(i + 1).padStart(2, '0')}</span>{c.name}</button>)}</div></div>}
      {showSettings && <div className="reader-panel settings-panel"><div className="panel-heading"><strong>阅读偏好</strong><Button isIconOnly variant="ghost" aria-label="关闭设置" onPress={() => setShowSettings(false)}><X size={18} /></Button></div><p>字号大小</p><div className="settings-row"><Button isIconOnly variant="outline" aria-label="缩小字号" isDisabled={fontSize <= 15} onPress={() => setFontSize(n => n - 1)}><Minus size={16} /></Button><span>{fontSize} px</span><Button isIconOnly variant="outline" aria-label="放大字号" isDisabled={fontSize >= 28} onPress={() => setFontSize(n => n + 1)}><Plus size={16} /></Button></div><p>阅读主题</p><div className="settings-row"><Button variant={theme === 'paper' ? 'primary' : 'outline'} onPress={() => setTheme('paper')}><Sun size={16} /> 纸张</Button><Button variant={theme === 'night' ? 'primary' : 'outline'} onPress={() => setTheme('night')}><Moon size={16} /> 夜间</Button></div></div>}
      {syncError && <ErrorNotice message={syncError} retry={() => void retryProgress()} />}
      <article className="reader-page"><div className="reader-overline">{selected?.name} <span> / </span> {String(chapterIndex + 1).padStart(2, '0')}</div><h1>{current?.name}</h1><div className="chapter-ornament">✳</div>{readingLoading ? <div className="center-loading"><Spinner /> 正在加载正文…</div> : readingError ? <ErrorNotice message={readingError} retry={() => void retryProgress()} /> : content ? <div className="chapter-body" style={{ fontSize: `${fontSize}px` }}>{content.split(/\n+/).map((paragraph, index) => <p key={index}>{paragraph}</p>)}</div> : <div className="empty-reading">本章节暂无正文内容。</div>}
      {!readingLoading && <div className="chapter-navigation"><Button variant="outline" isDisabled={chapterIndex === 0} onPress={() => void readChapter(chapterIndex - 1)}><ChevronLeft size={17} /> 上一章</Button><span>{chapterIndex + 1} / {chapters.length}</span><Button variant="primary" isDisabled={chapterIndex >= chapters.length - 1} onPress={() => void readChapter(chapterIndex + 1)}>下一章 <ChevronRight size={17} /></Button></div>}</article>
      <footer className="reader-footer">拾页 · 给每一段故事一个安静的角落</footer>
    </main> : <main className="main-content"><header className="topbar"><Button isIconOnly variant="ghost" className="menu-button" aria-label="打开菜单" onPress={() => setMobileNav(true)}><Menu size={22} /></Button><div className="breadcrumbs">阅读空间 <ChevronRight size={14} /> <strong>{view === 'shelf' ? '我的书架' : view === 'discover' ? '发现好书' : '书籍详情'}</strong></div><div className="topbar-right"><span className="topbar-date">让阅读成为日常</span><div className="user-mark"><BookOpen size={18} /></div></div></header>
      <div className="page-content">{libraryError && <ErrorNotice message={libraryError} retry={() => void reloadLibrary()} />}{view === 'shelf' && <>
        {legacy && !importMessage && <div className="notice" role="status">检测到旧浏览器书架（{legacy.books.length} 本）。导入将逐本合并至服务端，旧数据会保留。<Button variant="outline" isDisabled={importing} onPress={() => void importLegacy()}>确认导入</Button><Button variant="ghost" onPress={() => setLegacy(null)}>暂不导入</Button></div>}
        {importMessage && <ErrorNotice message={importMessage} retry={legacy && !importing ? () => void importLegacy() : undefined} />}
        <section className="page-heading"><div><div className="eyebrow">YOUR PERSONAL LIBRARY <span className="eyebrow-line" /></div><h1>我的书架<span className="heading-dot">.</span></h1><p>好故事，总值得慢慢读。</p></div><Button variant="primary" onPress={() => navigate('discover')}><Plus size={18} /> 寻找新故事</Button></section>
        <section className="feature-banner"><div className="feature-copy"><div className="feature-tag"><span className="pulse-dot" /> 阅读时光</div><h2>{recent && progress[bookKey(recent)] ? '故事还在继续，' : '翻开一本书，'}<br /><em>{recent && progress[bookKey(recent)] ? '从上次停下的地方。' : '去遇见另一个世界。'}</em></h2><p>{recent && progress[bookKey(recent)] ? `上次读到 · ${recent.name} · ${progress[bookKey(recent)].chapterName}` : '你的私人书架已准备就绪。搜索一本喜欢的书，从第一页开始。'}</p><Button variant="secondary" onPress={() => recent ? void openBook(recent) : navigate('discover')}>{recent ? '继续阅读' : '探索书籍'} <ArrowRight size={17} /></Button></div><div className="feature-art"><div className="art-circle" /><div className="art-book art-book-back" /><div className="art-book art-book-front"><BookOpen size={54} strokeWidth={1} /><span>THE WORLD<br />BETWEEN<br />PAGES</span><i>✳</i></div></div></section>
        <section className="section-heading"><div><span className="section-kicker">COLLECTION</span><h2>书架藏书 <span className="count-badge">{books.length}</span></h2></div><span className="section-hint">每一本都有自己的故事</span></section>
        {books.length ? <div className="book-grid">{books.map(book => <button className="book-card" key={bookKey(book)} onClick={() => void openBook(book)}><Cover book={book} /><div className="card-meta"><strong>{book.name}</strong><span>{book.author || '作者未知'}</span><small>{progress[bookKey(book)] ? `读至 ${progress[bookKey(book)].chapterName}` : '尚未开始阅读'}</small></div></button>)}</div> : <div className="empty-state"><div className="empty-icon"><BookMarked size={35} strokeWidth={1.3} /></div><h3>书架还是空的</h3><p>从发现页搜索喜欢的书，加入书架，开始属于你的阅读旅程。</p><Button variant="primary" onPress={() => navigate('discover')}>去发现好书 <ArrowRight size={17} /></Button></div>}
      </>}{view === 'discover' && <>
        <section className="page-heading"><div><div className="eyebrow">FIND YOUR NEXT STORY <span className="eyebrow-line" /></div><h1>发现好书<span className="heading-dot">.</span></h1><p>下一段心动的故事，从这里开始。</p></div></section>
        <form className="search-form" onSubmit={e => { e.preventDefault(); void search() }}><Search size={21} /><TextField aria-label="搜索书名或作者" value={query} onChange={setQuery}><Input placeholder="搜索书名，开启一段阅读旅程…" /></TextField><Button type="submit" variant="primary" isDisabled={loading || !query.trim()}>{loading ? '搜索中…' : '搜索书籍'} <ArrowRight size={16} /></Button></form>
        <section className="section-heading"><div><span className="section-kicker">EXPLORE</span><h2>{searched ? `“${searched}” 的搜索结果` : '寻找你的下一本书'}</h2></div>{searched && !loading && !error && <span className="section-hint">找到 {results.length} 本书</span>}</section>
        {error ? <ErrorNotice message={error} retry={() => void search(searched)} /> : loading ? <div className="center-loading"><Spinner /> 正在书海中寻找…</div> : results.length ? <div className="book-grid">{results.map(book => <button className="book-card" key={bookKey(book)} onClick={() => void openBook(book)}><Cover book={book} /><div className="card-meta"><strong>{book.name}</strong><span>{book.author || '作者未知'}</span><small>{book.classify || book.status || '查看书籍详情'}</small></div></button>)}</div> : <div className="empty-state"><div className="empty-icon"><Search size={33} strokeWidth={1.3} /></div><h3>{searched ? '没有找到匹配的书籍' : '书海浩瀚，从搜索开始'}</h3><p>{searched ? '试试换一个书名或作者，也许会有新的发现。' : '输入书名或作者，搜索实时书源；结果会在这里呈现。'}</p></div>}
      </>}{view === 'detail' && selected && <>
        <Button variant="ghost" className="back-link" onPress={() => navigate(books.some(b => bookKey(b) === bookKey(selected)) ? 'shelf' : 'discover')}><ArrowLeft size={17} /> 返回{saved ? '书架' : '搜索'}</Button>
        <div className="detail-hero"><Cover book={selected} large /><div className="detail-info"><span className="section-kicker">BOOK DETAILS · 书籍详情</span><h1>{selected.name}</h1><div className="detail-author">{selected.author || '作者未知'} <span className="metadata-divider">/</span> {selected.classify || '小说'}</div><div className="detail-tags">{selected.status && <span>{selected.status}</span>}{selected.size && <span>{selected.size}</span>}{selected.source_id && <span>书源 {selected.source_id}</span>}</div><p className="detail-intro">{selected.introduce || '暂无简介。打开目录，发现这本书的故事。'}</p><div className="detail-actions"><Button variant="primary" isDisabled={catalogLoading || !chapters.length} onPress={() => resume(selected)}><BookOpen size={18} /> {progress[bookKey(selected)] ? '继续阅读' : '开始阅读'}</Button><Button variant="outline" isDisabled={busy} onPress={() => void (saved ? removeBook(selected) : addBook(selected))}>{saved ? <Check size={17} /> : <Bookmark size={17} />}{saved ? '已在书架' : '加入书架'}</Button>{saved && <Button isIconOnly variant="ghost" aria-label="从书架移除" isDisabled={busy} onPress={() => void removeBook(selected)}><Trash2 size={17} /></Button>}</div></div></div>
        <section className="section-heading catalog-heading"><div><span className="section-kicker">CHAPTERS</span><h2>章节目录 <span className="count-badge">{chapters.length}</span></h2></div><span className="section-hint">点击章节直接开始阅读</span></section>
        {catalogError ? <ErrorNotice message={catalogError} retry={() => void openBook(selected)} /> : catalogLoading ? <div className="center-loading"><Spinner /> 正在整理章节目录…</div> : chapters.length ? <div className="chapter-list">{chapters.map((chapter, index) => <button className="chapter-row" key={chapter.url} onClick={() => void readChapter(index)}><span className="chapter-number">{String(index + 1).padStart(2, '0')}</span><span className="chapter-name">{chapter.name}</span>{progress[bookKey(selected)]?.chapterUrl === chapter.url && <span className="chapter-current">上次读到</span>}<ChevronRight size={17} /></button>)}</div> : <div className="empty-state"><div className="empty-icon"><List size={33} /></div><h3>暂无章节</h3><p>这个书源暂时没有提供章节内容。</p></div>}
      </>}</div><footer className="page-footer">拾页 W · READER <span>一个安放故事的地方</span></footer></main>}
  </div>
}
export default App