import { PrismaClient } from '@prisma/client'
import { PrismaD1 } from '@prisma/adapter-d1'

export * from '@prisma/client'

declare global {
  var __prisma: PrismaClient | undefined
}

export function getPrisma(d1Database?: D1Database): PrismaClient {
  let prisma: PrismaClient

  if (d1Database) {
    // Cloudflare Workers environment with D1
    const adapter = new PrismaD1(d1Database)
    prisma = new PrismaClient({ adapter })
  } else {
    // Local development with SQLite
    if (globalThis.__prisma) {
      return globalThis.__prisma
    }
    prisma = new PrismaClient()
    globalThis.__prisma = prisma
  }

  return prisma
}

export default getPrisma