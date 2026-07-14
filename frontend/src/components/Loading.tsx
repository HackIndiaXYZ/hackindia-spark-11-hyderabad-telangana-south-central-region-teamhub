import { Loader2 } from 'lucide-react'

interface LoadingProps {
  text?: string
  fullPage?: boolean
  size?: number
}

export default function Loading({ text = 'Loading...', fullPage = false, size = 24 }: LoadingProps) {
  const content = (
    <div className={`loading-spinner ${fullPage ? 'full-page' : ''}`}>
      <Loader2 size={size} className="spin" />
      <span>{text}</span>
    </div>
  )
  return content
}
