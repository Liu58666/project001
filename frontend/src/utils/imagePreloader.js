/**
 * 图片预加载工具
 * 在数据加载完成后立即开始预加载图片，减少用户感知的加载时间
 */

// 图片缓存状态
const imageCache = new Map()

/**
 * 预加载单张图片
 * @param {string} url - 图片URL
 * @returns {Promise<string>} - 返回加载成功的URL
 */
export function preloadImage(url) {
  if (!url) return Promise.resolve('')
  
  // 如果已经缓存，直接返回
  if (imageCache.has(url)) {
    return imageCache.get(url)
  }
  
  const promise = new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(url)
    img.onerror = () => reject(new Error(`Failed to load: ${url}`))
    img.src = url
  })
  
  imageCache.set(url, promise)
  return promise
}

/**
 * 批量预加载图片（带并发控制）
 * @param {string[]} urls - 图片URL数组
 * @param {number} concurrency - 并发数，默认4
 * @returns {Promise<Map<string, boolean>>} - 返回每个URL的加载状态
 */
export async function preloadImages(urls, concurrency = 4) {
  const validUrls = urls.filter(url => url && typeof url === 'string')
  const results = new Map()
  
  if (validUrls.length === 0) return results
  
  // 分批处理
  for (let i = 0; i < validUrls.length; i += concurrency) {
    const batch = validUrls.slice(i, i + concurrency)
    const promises = batch.map(url => 
      preloadImage(url)
        .then(() => ({ url, success: true }))
        .catch(() => ({ url, success: false }))
    )
    
    const batchResults = await Promise.all(promises)
    batchResults.forEach(({ url, success }) => {
      results.set(url, success)
    })
  }
  
  return results
}

/**
 * 预加载图片（不等待完成，后台加载）
 * @param {string[]} urls - 图片URL数组
 */
export function preloadImagesInBackground(urls) {
  const validUrls = urls.filter(url => url && typeof url === 'string')
  validUrls.forEach(url => {
    if (!imageCache.has(url)) {
      const img = new Image()
      const promise = new Promise((resolve) => {
        img.onload = () => resolve(url)
        img.onerror = () => resolve('') // 失败也resolve，不阻塞
      })
      imageCache.set(url, promise)
      img.src = url
    }
  })
}

/**
 * 检查图片是否已缓存/加载
 * @param {string} url - 图片URL
 * @returns {boolean}
 */
export function isImageCached(url) {
  return imageCache.has(url)
}

/**
 * 清除图片缓存
 */
export function clearImageCache() {
  imageCache.clear()
}
