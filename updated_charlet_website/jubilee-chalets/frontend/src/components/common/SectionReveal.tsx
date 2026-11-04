import { ReactNode } from 'react'
import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'

interface Props {
  children: ReactNode
  delay?: number
  className?: string
}

export default function SectionReveal({ children, delay = 0, className }: Props) {
  const { ref, inView } = useInView({ triggerOnce: true, threshold: 0.1 })
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 24 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.55, delay, ease: 'easeOut' }}
      className={className}
    >
      {children}
    </motion.div>
  )
}
