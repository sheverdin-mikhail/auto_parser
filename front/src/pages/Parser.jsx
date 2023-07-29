import axios from 'axios'
import React, { useContext, useEffect, useState } from 'react'
import MyButton from '../components/UI/MyButton/MyButton'
import MyTable from '../components/UI/MyTable/MyTable'
import { AxiosConfig } from '../config'
import { AuthContext } from '../context'
import '../styles/Parser.css'

export default function Parser() {

  const [drag, setDrag] = useState(false)
  const {isAuth} = useContext(AuthContext)
  const {setIsAuth} = useContext(AuthContext)


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
    let files = [...e.dataTransfer.files]
    const formData = new FormData()
    formData.append('file', files[0])
    const params = {
      headers: {
        'Authorization': `${AxiosConfig.secret_string} ${isAuth.access}`
      }
    }
    axios.post(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/v1/input_files/`, formData, params)
    .then((response)=>{
      fetchTableData()
    })
    .catch((err)=>{
      if (err.response.status === 401){
        localStorage.removeItem(isAuth)
        setIsAuth({auth:false})
      }
    })
    setDrag(false)
  }


  const [tableData, setTableData] = useState([
  ])
  
  function fetchTableData(){
    const params = {
      headers: {
        'Authorization': `${AxiosConfig.secret_string} ${isAuth.access}`
      }
    }
      axios.get(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/v1/parser_task_list/`, params)
      .then(response=>{
        setTableData(response.data)
      })
      .catch((err)=>{
        if (err.response.status === 401){
          localStorage.removeItem(isAuth)
          setIsAuth({auth:false})
        }
      })
      
  }

  function deleteTableRow(row){
    const params = {
      headers: {
        'Authorization': `${AxiosConfig.secret_string} ${isAuth.access}`
      }
    }
    axios.delete(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/v1/parser_task/${row}`, params)
    .then(response=>{
      fetchTableData()
    })
    .catch(err=>{
      if (err.response.status === 401){
        localStorage.removeItem(isAuth)
        setIsAuth({auth:false})
      }
    })  
  }

  function runTaskParser(task){
    const params = {
      headers: {
        'Authorization': `${AxiosConfig.secret_string} ${isAuth.access}`
      }
    }
    const formData = new FormData()
    formData.append('status', 'run')
    axios.put(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/v1/parser_task/${task}/`, formData, params)
    .then(response=>{
      fetchTableData()
    })
    .catch((err)=>{
      if (err.response.status === 401){
        localStorage.removeItem(isAuth)
        setIsAuth({auth:false})
      }
    })
  }

  function saveTaskSites(data){
    const params = {
      headers: {
        'Authorization': `${AxiosConfig.secret_string} ${isAuth.access}`
      },
    }
    const formData = new FormData()
    data['sites'].forEach(element => {
      formData.append('sites', element)
    });

    axios.put(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/v1/change_sites/${data['id']}/`, formData, params)
    .then(response=>{
      fetchTableData()
    })
    .catch((err)=>{
      if (err.response.status === 401){
        localStorage.removeItem(isAuth)
        setIsAuth({auth:false})
      }
    })
  }
  function saveTaskMarker(data){
    const params = {
      headers: {
        'Authorization': `${AxiosConfig.secret_string} ${isAuth.access}`
      },
    }
    const formData = new FormData()
    formData.append('marker', data['marker'])
    axios.put(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/v1/change_marker/${data['id']}/`, formData, params)
    .then(response=>{
      fetchTableData()
    })
    .catch((err)=>{
      if (err.response.status === 401){
        localStorage.removeItem(isAuth)
        setIsAuth({auth:false})
      }
    })
  }
  
  async function downloadParserdResult(id){
    const params = {
      headers: {
        'Authorization': `${AxiosConfig.secret_string} ${isAuth.access}`
      }
    }
    const response = await fetch(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/v1/download/${id}/`, params)
    if(response.status === 200){
      const blob = await response.blob()
      const href = window.URL.createObjectURL(blob);
      // create "a" HTLM element with href to file & click
      const link = document.createElement('a');
      link.href = href;
      link.download = `${id}_output.xlsx`
      document.body.appendChild(link);
      link.click();

      // clean up "a" element & remove ObjectURL
      document.body.removeChild(link);
      URL.revokeObjectURL(href);
    }
  }


  useEffect(() => {
      fetchTableData()
  }, [])
  

  return (
    <div>
      <MyButton 
        style={{'margin': '40px 0 25px 0'}} 
        className="loadButton" 
        onDragStart={
          e=> dragStartHandler(e)
        }
        onDragOver={
          e=>dragStartHandler(e)
        }
        >Перенесите файл для загрузки</MyButton>
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
              
            : <MyTable deleteRow={deleteTableRow} runTask={runTaskParser} saveSites={saveTaskSites} saveMarker={saveTaskMarker} tableData={tableData} downloadResult={downloadParserdResult}>
                <thead>
                  <tr>
                      <th>
                          id
                      </th>
                      <th>
                          Загруженный файл
                      </th>
                      <th>
                          Дата
                      </th>
                      <th>
                          Маркер
                      </th>
                      <th>
                          Кол-во заданий
                      </th>
                      <th>
                          Состояние
                      </th>
                      <th>
                          Сайты
                      </th>
                      <th>
                          Результат
                      </th>
                      <th>
                      </th>
                      <th>
                      </th>
                  </tr>
              </thead>
            </MyTable>
        }
    </div>
  )
}


