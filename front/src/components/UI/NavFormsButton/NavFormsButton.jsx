import React from 'react'
import './NavFormsButton.module.css'

export default function NavFormsButton({children, className, ...props}) {
  return (
    <button className={`NavFormsButton ${className}`} {...props} >{children}</button>
  )
}
