import React, { useContext } from 'react'
import { NavLink } from 'react-router-dom'
import { AuthContext } from '../context'

import '../styles/Navbar.css'

export default function Navbar({username}) {

  const {isAuth} = useContext(AuthContext)
  return (
    <div className='nav'>
        <NavLink className='nav__link' to="/main">Главная</NavLink>
        <NavLink className='nav__link' to="/control">Управление</NavLink>
        <NavLink className='nav__link' to="/parser">Парсер</NavLink>
        <NavLink className='nav__link' to="/api-panel">API</NavLink>
        <NavLink className='nav__link' to={
            isAuth.username
            ?
            '/root'
            :
            '/login'
          }>
          {
            isAuth.username
            ?
            isAuth.username
            :
            'Войти'
          }
        </NavLink>
    </div>
  )
}
