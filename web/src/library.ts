export interface Novel {
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

export const bookKey = (book: Novel) => `${book.source_id ?? ''}::${book.url}`
const storageKey = 'wreader-library-v1'
const progressKey = 'wreader-progress-v1'

function stored<T>(key: string, fallback: T): T {
  try { return JSON.parse(localStorage.getItem(key) || '') as T } catch { return fallback }
}

export function loadBooks(): Novel[] {
  const value = stored<unknown>(storageKey, [])
  return Array.isArray(value) ? value.filter((item): item is Novel => !!item && typeof item.name === 'string' && typeof item.url === 'string') : []
}
export function loadProgress(): ProgressMap {
  const value = stored<unknown>(progressKey, {})
  return value && typeof value === 'object' && !Array.isArray(value) ? value as ProgressMap : {}
}
export function saveBooks(value: Novel[]) { try { localStorage.setItem(storageKey, JSON.stringify(value)) } catch { /* Storage is optional. */ } }
export function saveProgress(value: ProgressMap) { try { localStorage.setItem(progressKey, JSON.stringify(value)) } catch { /* Storage is optional. */ } }

async function json<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init)
  if (!response.ok) throw new Error(`请求失败（${response.status}），请稍后重试`)
  return response.json() as Promise<T>
}
export function searchBooks(keyword: string): Promise<Novel[]> {
  return json(`/novel/search?${new URLSearchParams({ keyword })}`)
}
async function post<T>(path: string, body: object): Promise<T> {
  return json(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
}

// Sources paginate with URLs; guard against cycles and overly long catalogs.
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