import React, { useContext } from 'react'
import MyButton from '../components/UI/MyButton/MyButton'
import { AuthContext } from '../context'

export default function Root() {
    const {setIsAuth} = useContext(AuthContext)
  return (
    <div>
        <MyButton onClick={e=>{
            setIsAuth({auth:false})
            localStorage.removeItem('isAuth')
        }} >Выйти</MyButton>
    </div>
  )
}
