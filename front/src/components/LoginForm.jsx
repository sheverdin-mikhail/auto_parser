import axios from 'axios'
import React, { useContext, useState } from 'react'
import { AxiosConfig } from '../config'
import { AuthContext } from '../context'
import MyButton from './UI/MyButton/MyButton'

export default function LoginForm() {

    const {setIsAuth} = useContext(AuthContext)
    const [authError, setAuthError] = useState(null)

    function getAuthToken(e){
        e.preventDefault()
        let username = document.forms[0]['username'].value 
        axios.post(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/token/`, new FormData(document.forms[0]))
        .then(response => {
            const data = response.data
            setIsAuth({auth: true, access: data.access, refresh: data.refresh, username: username})
            localStorage.setItem('isAuth', JSON.stringify({auth: true, access: data.access, refresh: data.refresh, username: username}))
        })
        .catch(err=>setAuthError())

    }


  return (
    <form className='form' style={{minWidth: '30%'}} onSubmit={e=>{getAuthToken(e)}}>
        <h3 className='form__header' style={{marginLeft: '0', alignSelf: 'center'}}>Вход</h3>
        {
            authError
            ?
            <div className='errMessage' style={{margin: '15px 0'}}>
                Неверно введено имя пользователя или пароль
            </div>
            :
            null
        }
        <label htmlFor="username" className="form__label">
            Логин
            <input type="text" name='username' id='username' className="form__input" />
        </label>
        <label htmlFor="password" className="form__label" >
            Пароль
            <input id='password' type="password" className="form__input" name="password"/>
        </label>
        <MyButton className="" type="submit" style={{backgroundColor: '#FF00F5', color: '#fff', border: 'none', marginTop: '15px'}} >Войти</MyButton>
        
    </form>
    
  )
}
