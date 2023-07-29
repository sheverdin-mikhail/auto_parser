import React from 'react'
import './MyButton.module.css'

export default function MyButton({children, className, ...props}) {
  return (
    <button className={`myButton ${className}`} {...props} >{children}</button>
  )
}
