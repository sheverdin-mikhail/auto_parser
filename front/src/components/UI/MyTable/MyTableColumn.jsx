import React from 'react'

export default function MyTableColumn({...props}) {
  return (
    <td>
        {
            typeof props.children === 'object'
            ?
            props.children['file']
            :
            props.children
        }
    </td>
  )
}
