import React, { useContext } from 'react'
import MyButton from './UI/MyButton/MyButton'
import '../styles/Form.css'
import axios from 'axios'
import { AuthContext } from '../context'
import { AxiosConfig } from '../config'

export default function AddProxyForm({getData}) {

    
    const {isAuth} = useContext(AuthContext)
    const {setIsAuth} = useContext(AuthContext)

    function addProxy(e){
        e.preventDefault()

        const params = {
            headers: {
              'Authorization': `${AxiosConfig.secret_string} ${isAuth.access}`
            }
          }
        const form = document.forms[0]
        const form_data = new FormData()
        form_data.append('type', form['type'].value)
        form_data.append('ip', form['ip_port'].value.split(':')[0])
        form_data.append('port', form['ip_port'].value.split(':')[1])
        form_data.append('login', form['login'].value)
        form_data.append('password', form['password'].value)
        axios.post(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/v1/proxies/`, form_data, params)
        .then(response => {
            getData()
        })
        .catch(err=>{
            console.log(err)
        })
    }

    return (
    <form className='form' onSubmit={e => addProxy(e)}>
        <h3 className='form__header'>Добавление прокси</h3>
        <label htmlFor="type" className="form__label">
            Тип прокс
            <select name="type" id="type" defaultValue={'null'} className="form__input form__select">
                <option value="null" hidden ></option>
                <option value="http">http</option>
                <option value="https">https</option>
            </select>
        </label>
        <label htmlFor="ip_port" className="form__label" >
            IP:Порт
            <input id='ip_port' type="text" className="form__input" name="ip_port" placeholder='127.0.0.1:8000'/>
        </label>
        <label htmlFor="login" className="form__label">
            Логин
            <input id='login' type="text" className="form__input" name='login'/>
        </label>
        <label htmlFor="password" className="form__label">
            Пароль
            <input id='password' type="text" className="form__input" name='password'/>
        </label>
        <MyButton className="addButton" type="submit" >Добавить</MyButton>
    </form>
    )
}
