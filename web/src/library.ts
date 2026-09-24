export interface Novel {
  book_id?: number
  name: string
  url: string
  source_id?: string | null
  author?: string | null
  size?: string | null
  status?: string | null
  cover_url?: string | null
  classify?: string | null
  introduce?: string | null
  last_update_time?: string | null
  last_chapter_name?: string | null
}
export interface Chapter { name: string; url: string }
export interface Progress { chapterUrl: string; chapterName: string; index: number; updatedAt: number }
export type ProgressMap = Record<string, Progress>
export interface ServerProgress { chapter_url: string; chapter_name: string; chapter_index: number; updated_at: number }
export interface ServerBook extends Novel { book_id: number; progress: ServerProgress | null }
export const bookKey = (book: Novel) => `${book.source_id ?? ''}::${book.url}`
export const toProgress = (item: ServerProgress): Progress => ({ chapterUrl: item.chapter_url, chapterName: item.chapter_name, index: item.chapter_index, updatedAt: item.updated_at })

// Legacy browser data stays untouched for recovery and retry.
export function legacyData(): { books: Novel[]; progress: ProgressMap; skipped: number } | null {
  const rawBooks = localStorage.getItem('wreader-library-v1')
  const rawProgress = localStorage.getItem('wreader-progress-v1')
  if (rawBooks === null && rawProgress === null) return null
  let books: unknown, progress: unknown
  try { books = rawBooks === null ? [] : JSON.parse(rawBooks); progress = rawProgress === null ? {} : JSON.parse(rawProgress) } catch { throw new Error('旧书架数据格式错误，请先备份浏览器数据') }
  if (!Array.isArray(books) || !progress || typeof progress !== 'object' || Array.isArray(progress)) throw new Error('旧书架数据格式错误，请先备份浏览器数据')
  const valid = books.filter((item): item is Novel => !!item && typeof item === 'object' && typeof item.name === 'string' && typeof item.url === 'string' && typeof item.source_id === 'string' && item.source_id.length === 32 && item.name.length > 0 && item.url.length > 0)
  return { books: valid, progress: progress as ProgressMap, skipped: books.length - valid.length }
}

let token: string | null = null
export function setToken(value: string | null) { token = value }
export class UnauthorizedError extends Error {}
async function json<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, { ...init, headers: { ...init?.headers, ...(token ? { Authorization: `Bearer ${token}` } : {}) } })
  if (response.status === 401 && url !== '/api/auth/login') { setToken(null); window.dispatchEvent(new Event('wreader-unauthorized')); throw new UnauthorizedError('登录已失效，请重新登录') }
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null
    throw new Error(typeof body?.detail === 'string' ? body.detail : `请求失败（${response.status}），请稍后重试`)
  }
  return response.status === 204 ? undefined as T : response.json() as Promise<T>
}
export async function login(password: string): Promise<void> {
  const result = await json<{ access_token: string }>('/api/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ password }) })
  setToken(result.access_token)
}
export const getLibrary = () => json<{ books: ServerBook[] }>('/api/library')
export const addToLibrary = (book: Novel) => json<ServerBook>('/api/library/books', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(book) })
export const removeFromLibrary = (id: number) => json<void>(`/api/library/books/${id}`, { method: 'DELETE' })
export const putProgress = (id: number, chapter: Chapter, index: number, migrated?: number) => json<ServerProgress>(`/api/library/books/${id}/progress`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ chapter_url: chapter.url, chapter_name: chapter.name, chapter_index: index, ...(migrated === undefined ? {} : { migrated_updated_at: migrated }) }) })
export function searchBooks(keyword: string): Promise<Novel[]> { return json(`/novel/search?${new URLSearchParams({ keyword })}`) }
async function post<T>(path: string, body: object): Promise<T> { return json(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }) }

export async function getChapters(book: Novel): Promise<Chapter[]> {
  const chapters: Chapter[] = []
  const seenPages = new Set<string>()
  const seenChapters = new Set<string>()
  let nextPage: string | undefined
  for (let page = 0; page < 40; page++) {
    const current = nextPage || book.url
    if (seenPages.has(current)) break
    seenPages.add(current)
    const result: { chapter_list: Chapter[]; next_page: string } = await post('/novel/chapter', { novel: book, next_page: nextPage ?? null })
    for (const chapter of result.chapter_list ?? []) {
      if (!chapter.url || seenChapters.has(chapter.url)) continue
      seenChapters.add(chapter.url)
      chapters.push(chapter)
    }
    nextPage = result.next_page || undefined
    if (!nextPage) break
  }
  return chapters
}
export async function getContent(book: Novel, chapter: Chapter): Promise<string> {
  const parts: string[] = []
  const seen = new Set<string>()
  let nextPage: string | undefined
  for (let page = 0; page < 30; page++) {
    const current = nextPage || chapter.url
    if (seen.has(current)) break
    seen.add(current)
    const result: { content: string; next_page: string } = await post('/novel/content', { novel: book, chapter, next_page: nextPage ?? null })
    if (result.content) parts.push(result.content)
    nextPage = result.next_page || undefined
    if (!nextPage) break
  }
  return parts.join('\n\n')
}