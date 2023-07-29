import axios from 'axios'
import React, { useContext, useEffect, useState } from 'react'
import MyButton from '../components/UI/MyButton/MyButton'
import MyTable from '../components/UI/MyTable/MyTable'
import { AxiosConfig } from '../config'
import { AuthContext } from '../context'
import '../styles/Parser.css'

export default function Api() {

  const {isAuth} = useContext(AuthContext)
  const {setIsAuth} = useContext(AuthContext)


  const [tableData, setTableData] = useState([
  ])
  
  function fetchTableData(){
    const params = {
      headers: {
        'Authorization': `${AxiosConfig.secret_string} ${isAuth.access}`
      }
    }
      axios.get(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/v2/parser_task_list/`, params)
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
    axios.delete(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/v2/parser_task/${row}`, params)
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

    axios.patch(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/v2/parser_task/${data['id']}/`, formData, params)
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
    axios.patch(`${AxiosConfig.http_header}${AxiosConfig.domain}/api/v2/parser_task/${data['id']}/`, formData, params)
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
  


  useEffect(() => {
      fetchTableData()
  }, [])
  

  return (
    <div>
        <MyTable deleteRow={deleteTableRow} saveSites={saveTaskSites} saveMarker={saveTaskMarker} tableData={tableData}>
                <thead>
                  <tr>
                      <th>
                          id
                      </th>
                      <th>
                          Сайты
                      </th>
                      <th>
                          Дата создания
                      </th>
                      <th>
                          Маркер
                      </th>
                      <th>
                          Кол-во заданий
                      </th>
                      <th>
                          Сайты
                      </th>
                      <th>
                      </th>
                      
                  </tr>
              </thead>
        </MyTable>
    </div>
  )
}


