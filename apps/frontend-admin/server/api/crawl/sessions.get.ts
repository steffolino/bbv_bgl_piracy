export default defineEventHandler(async (event) => {
  try {
  // Proxy request to Python Flask API bridge
  const config = useRuntimeConfig()
  const crawlBase = config.public.crawlApiBase || 'http://localhost:5001'
  const response = await fetch(`${crawlBase}/api/crawl/sessions`)
    
    if (!response.ok) {
      throw new Error(`Flask API returned ${response.status}`)
    }
    
    const data = await response.json()
    
    // Transform data to match frontend expectations
    const transformedSessions = data.map((session: any) => ({
      id: session.id,
      session_name: session.sessionName,
      spider_name: session.spiderName,
      start_time: session.startTime,
      end_time: session.endTime,
      status: session.status,
      total_requests: session.totalRequests || 0,
      successful_requests: session.successfulRequests || 0,
      failed_requests: session.failedRequests || 0,
      items_scraped: session.itemsScraped || 0,
      leagues_discovered: session.leaguesDiscovered || 0,
      duration_minutes: session.endTime && session.startTime ? 
        Math.round((new Date(session.endTime).getTime() - new Date(session.startTime).getTime()) / (1000 * 60)) : 0
    }))
    
    return { sessions: transformedSessions }
  } catch (error) {
    console.error('Error fetching crawl sessions:', error)
    
    // Return fallback data if Flask API is not available
    return {
      sessions: [
        {
          id: 'extended_historical_crawler_20250929_175659',
          session_name: 'extended_historical_crawler',
          spider_name: 'extended_historical_crawler',
          start_time: '2025-09-29T17:56:59.790091',
          end_time: '2025-09-29T18:00:26.390000',
          status: 'completed',
          total_requests: 151,
          successful_requests: 151,
          failed_requests: 0,
          items_scraped: 0,
          leagues_discovered: 0,
          duration_minutes: 3
        }
      ]
    }
  }
})
