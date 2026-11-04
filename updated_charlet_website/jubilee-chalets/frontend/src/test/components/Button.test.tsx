import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import Button from '@/components/ui/Button'

describe('Button', () => {
  it('renders children text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('fires onClick handler', () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Submit</Button>)
    fireEvent.click(screen.getByText('Submit'))
    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('is disabled when loading', () => {
    render(<Button isLoading>Save</Button>)
    const btn = screen.getByRole('button')
    expect(btn).toBeDisabled()
  })

  it('is disabled when disabled prop is set', () => {
    render(<Button disabled>Save</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('applies variant classes correctly', () => {
    const { rerender } = render(<Button variant="secondary">Click</Button>)
    expect(screen.getByRole('button').className).toContain('btn-secondary')

    rerender(<Button variant="danger">Delete</Button>)
    expect(screen.getByRole('button').className).toContain('bg-red-600')
  })

  it('applies full width class', () => {
    render(<Button fullWidth>Submit</Button>)
    expect(screen.getByRole('button').className).toContain('w-full')
  })
})
