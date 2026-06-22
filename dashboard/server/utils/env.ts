import fs from 'node:fs'
import path from 'node:path'

/**
 * Parses and returns key-value pairs from the parent directory's .env file.
 */
export function getParentEnv(): Record<string, string> {
  const envPath = path.resolve(process.cwd(), '../.env')
  if (!fs.existsSync(envPath)) {
    return {}
  }
  try {
    const content = fs.readFileSync(envPath, 'utf-8')
    const config: Record<string, string> = {}
    
    for (const line of content.split('\n')) {
      const trimmed = line.trim()
      if (!trimmed || trimmed.startsWith('#')) continue
      
      const firstEqual = trimmed.indexOf('=')
      if (firstEqual === -1) continue
      
      const key = trimmed.substring(0, firstEqual).trim()
      let val = trimmed.substring(firstEqual + 1).trim()
      
      // Strip wrapping quotes if present
      if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
        val = val.substring(1, val.length - 1)
      }
      
      config[key] = val
    }
    
    return config
  } catch (error) {
    console.error('Error reading parent .env file:', error)
    return {}
  }
}
