export default defineEventHandler(async (event) => {
  try {
    const response = await fetch('https://unpkg.com/@lottiefiles/lottie-player@1.7.1/dist/lottie-player.js')
    if (!response.ok) {
      throw new Error('Failed to fetch from unpkg')
    }
    const scriptContent = await response.text()
    
    setResponseHeader(event, 'Content-Type', 'application/javascript; charset=utf-8')
    setResponseHeader(event, 'Cache-Control', 'public, max-age=31536000, immutable')
    
    return scriptContent
  } catch (error) {
    console.error('Error proxying lottie-player.js:', error)
    // Fallback to older version from cdnjs if unpkg fails on backend
    try {
      const fallback = await fetch('https://cdnjs.cloudflare.com/ajax/libs/lottie-player/1.4.3/lottie-player.js')
      const fallbackContent = await fallback.text()
      setResponseHeader(event, 'Content-Type', 'application/javascript; charset=utf-8')
      setResponseHeader(event, 'Cache-Control', 'public, max-age=31536000, immutable')
      return fallbackContent
    } catch (e) {
      throw createError({ statusCode: 500, statusMessage: 'Failed to proxy lottie-player script' })
    }
  }
})
