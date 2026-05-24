import styles from './MarkdownContent.module.css'


type MarkdownBlock =
  | { type: 'h1' | 'h2' | 'h3' | 'p'; text: string }
  | { type: 'ul'; items: string[] }


function parseMarkdown(markdown: string): MarkdownBlock[] {
  const lines = markdown.split('\n')
  const blocks: MarkdownBlock[] = []
  let currentList: string[] = []

  function flushList() {
    if (currentList.length > 0) {
      blocks.push({ type: 'ul', items: currentList })
      currentList = []
    }
  }

  for (const rawLine of lines) {
    const line = rawLine.trim()
    if (!line) {
      flushList()
      continue
    }

    if (line.startsWith('- ') || line.startsWith('* ')) {
      currentList.push(line.slice(2).trim())
      continue
    }

    flushList()

    if (line.startsWith('### ')) {
      blocks.push({ type: 'h3', text: line.slice(4).trim() })
      continue
    }
    if (line.startsWith('## ')) {
      blocks.push({ type: 'h2', text: line.slice(3).trim() })
      continue
    }
    if (line.startsWith('# ')) {
      blocks.push({ type: 'h1', text: line.slice(2).trim() })
      continue
    }

    blocks.push({ type: 'p', text: line })
  }

  flushList()
  return blocks
}


export function MarkdownContent({ markdown }: { markdown: string }) {
  const blocks = parseMarkdown(markdown)

  return (
    <div className={styles.content}>
      {blocks.map((block, index) => {
        if (block.type === 'ul') {
          return (
            <ul key={`ul-${index}`}>
              {block.items.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          )
        }

        if (block.type === 'h1') {
          return <h1 key={`h1-${index}`}>{block.text}</h1>
        }
        if (block.type === 'h2') {
          return <h2 key={`h2-${index}`}>{block.text}</h2>
        }
        if (block.type === 'h3') {
          return <h3 key={`h3-${index}`}>{block.text}</h3>
        }

        return <p key={`p-${index}`}>{block.text}</p>
      })}
    </div>
  )
}
