import axios from 'axios'
import React, { useContext, useEffect, useState } from 'react'
import AddAccountForm from '../components/AddAccountForm'
import AddProxyForm from '../components/AddProxyForm'
import MyButton from '../components/UI/MyButton/MyButton'
import MyTable from '../components/UI/MyTable/MyTable'
import NavFormsButton from '../components/UI/NavFormsButton/NavFormsButton'
import { AxiosConfig } from '../config'
import { AuthContext } from '../context'
import '../styles/Control.css'


export default function Control() {

    const [drag, setDrag] = useState(false)
    const [activeForm, setActiveForm] = useState('proxy')
    const {isAuth} = useContext(AuthContext)
    const [tableData, setTableData] = useState([])
    const {setIsAuth} = useContext(AuthContext)

    function getProxiesData(){
      const params = {
        headers: {
          'Authorization': `${AxiosConfig.secret_string} ${isAuth.access}`
        }
      }
        axios.get(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/v1/proxies/`, params)
        .then(response => {
            localStorage.setItem('tableData', response.data)
            setTableData(response.data)
        })
        .catch(err => {
            if (err.response.status === 401){
              localStorage.removeItem(isAuth)
              setIsAuth({auth:false})
            }
        })
    }


    function dragStartHandler(e){
        e.preventDefault()
        setDrag(true)
      }
    
      function dragLeaveHandler(e){
        e.preventDefault()
        setDrag(false)
      }
    
      function dragDropHandler(e){
        e.preventDefault()
      }

    

    useEffect(() => {
        if (tableData.length !== 0){
            setTableData(tableData)
        }else{
            getProxiesData()
        }
        setActiveForm(localStorage.getItem('activeForm'))
    }, [])

    function setActiveFormHandler(form){
        setActiveForm(form)
        localStorage.setItem('activeForm', form)
    }
    
    function deleteTableRow(row){
      const params = {
        headers: {
          'Authorization': `${AxiosConfig.secret_string} ${isAuth.access}`
        }
      }
        axios.delete(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/v1/proxy/${row}`, params)
        .then(response=>{
          getProxiesData()
        })
        .catch(err=>{
          if (err.response.status === 401){
            localStorage.removeItem(isAuth)
            setIsAuth({auth:false})
          }
        })  
      }

  return (
    
    <div>
        <div className='controlTop'>
            <div className='formsBlock'>
                <div className="formsBlock__nav">
                    <NavFormsButton className={activeForm==='proxy'? 'active' : ''} onClick={() => setActiveFormHandler('proxy')}>Прокси</NavFormsButton>
                    <NavFormsButton className={''}>Сайт</NavFormsButton>
                    <NavFormsButton className={activeForm==='accounts'? 'active' : ''} onClick={() => setActiveFormHandler('accounts')}>Аккаунты</NavFormsButton>
                </div>
                <div className="formsBlock__form">
                    {
                        activeForm==='proxy'
                        ?
                        <AddProxyForm getData={getProxiesData}/>
                        :
                        <AddAccountForm/>
                    }
                </div>
            </div>
            <div className="uploadFileBlock">
                    <MyButton 
                style={{'margin': '40px 0 25px 0'}} 
                className="loadButton" 
                onDragStart={
                e=> dragStartHandler(e)
                }
                onDragLeave={
                e=>dragLeaveHandler(e)
                }
                onDragOver={
                e=>dragStartHandler(e)
                }
                >Перенесите файл для загрузки</MyButton>
                
            </div>
        </div> 
        {
                    drag
                    ? <div 
                      className='dragInfo' 
                      onDragStart={
                        e=> dragStartHandler(e)
                      }
                      onDragLeave={
                        e=>dragLeaveHandler(e)
                      }
                      onDragOver={
                        e=>dragStartHandler(e)
                      }
                      onDrop={
                        e=>dragDropHandler(e)
                      }
                    
                    >
                        Отпустите файл для загрузки  
                      </div>
                    :
        <div>
            <MyTable tableData={tableData} deleteRow={deleteTableRow}>
                <thead>
                    <tr>
                        <th>id</th>
                        <th>Тип прокси</th>
                        <th>IP</th>
                        <th>Порт</th>
                        <th>Логин</th>
                        <th>Пароль</th>
                        <th>Состояние</th>
                        <th></th>
                    </tr>
                </thead>
            </MyTable>
        </div>
}
    </div>
  )
}
