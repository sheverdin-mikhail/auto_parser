import React, { useContext, useEffect, useMemo, useState } from 'react'
import MyButton from './UI/MyButton/MyButton'
import { Select } from 'antd'
import { AuthContext } from '../context'
import axios from 'axios'
import { AxiosConfig } from '../config'


export default function AddAccountForm() {

  const [sites, setSites] = useState([])
  const [curSite, setCurSite] = useState()

  const {isAuth} = useContext(AuthContext)
  const {setIsAuth} = useContext(AuthContext)

  


  function getSitesList(){
    const params = {
        headers: {
          'Authorization': `${AxiosConfig.secret_string} ${isAuth.access}`
        }
      }
        axios.get(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/v1/parser_sites_list/`, params)
        .then(response=>{
            const SelectSiteOptions = response.data.map(el => {
                return {label: el['name'], value: el['id']}
            })
            setSites(SelectSiteOptions)
        })
        .catch((err)=>{
          if (err.response.status === 401){
            localStorage.removeItem(isAuth)
            setIsAuth({auth:false})
          }
        })
  }

  function addAccount(e){
    e.preventDefault()

    const params = {
        headers: {
          'Authorization': `${AxiosConfig.secret_string} ${isAuth.access}`
        }
      }
    const form = document.forms[0]
    const form_data = new FormData()
    form_data.append('login', form['login'].value)
    form_data.append('password', form['password'].value)
    form_data.append('site', curSite)
    axios.post(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/v1/site_users/`, form_data, params)
    .then(response => {
      form['login'].value = ''
      form['password'].value = ''
    })
    .catch(err=>{
        console.log(err)
    })
}


  useEffect(() => {
    getSitesList()
  }, [])

  return (
    <form className='form' onSubmit={e => addAccount(e)}>
        <h3 className='form__header'>Добавление аккаунта</h3>
        <label htmlFor="type" className="form__label">
            Логин
            <input type="text" className="form__input" name='login' />
        </label>
        <label htmlFor="password" className="form__label" >
            Пароль
            <input id='password' type="text" className="form__input" name="password"/>
        </label>
        <label htmlFor="site" className="form__label" >
            Сайт
            <Select
                style={{
                    width: '100%',
                }}
                options={sites}
                name="site"
                id='site'
                onChange={(value)=>{setCurSite(value)}}
            />
        </label>
        <MyButton className="addButton" type="submit" >Добавить</MyButton>
    </form>
  )
}
