import { Select } from 'antd'
import _default from 'antd/lib/time-picker'
import axios from 'axios'
import React, { useContext, useState } from 'react'
import { useMemo } from 'react'
import { AxiosConfig } from '../../../config'
import { AuthContext } from '../../../context'
import MyButton from '../MyButton/MyButton'

export default function MyTableRow({item,  deleteRow, runTask, downloadResult, saveSites, saveMarker}) {

    const [sites, setSites] = useState()
    const [markers, setMarkers] = useState([
        {label: 'Аналитика', value: "1"},
        {label: 'Наличие', value: "2"},
        {label: 'Api', value: "3"},
        {label: 'Техническое', value: "4"},
    ])
    const {isAuth} = useContext(AuthContext)
    const {setIsAuth} = useContext(AuthContext)
    const [CurSites, setCurSites] = useState(item['sites'])


    function runTaskHandler(){
        runTask(item['id'])
    }

    function deleteTaskHandler(){
        deleteRow(item['id'])
    }
    const ChangeSitesHandler = (value) => {
        setCurSites({sites: value})
        if (value.length !== 0 ){
            saveSites({id: parseInt(item['id']), sites: value})
        }
    }
    const ChangeMarkerHandler = (value) => {
        saveMarker({id:  parseInt(item['id']), marker: value})
    }

    useMemo(() => {
        getSitesList()
    }, [])

    function downloadResultHandler(){
        downloadResult(item['id'])
    }

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
    return (
    <tr key={item['id']}>
        {
        
        Object.keys(item).map(
            (el, index)=>{
                switch (el) {
                    case 'id':    
                    return <td key={`MyTableRowKey_${index}`}>
                            {item[el]}
                        </td>            
                    case 'create_date':
                        return  <td key={`MyTableRowKey_${index}`}>
                            {item[el]}
                        </td> 
                    case 'rows_count':
                        return  <td key={`MyTableRowKey_${index}`}>
                            {item[el]}
                        </td> 
                    case 'status':
                        return <td key={`MyTableRowKey_${index}`}>{
                                typeof item[el] === 'boolean'
                                ?
                                    item[el]
                                    ?
                                    'Вкл'
                                    :
                                    'Выкл'   
                                :
                                item[el]
                            }
                        </td>
                    case 'input_file':
                        return  el.search(/file/) !== -1
                        ?
                        <td key={`MyTableRowKey_${index}`}>
                            <a href={
                                item[el]['file']||item[el].replace('http', 'https')
                            }>Скачать файл</a>
                        </td>
                        :
                        null
                    case 'sites':
                        return <td key={`MyTableRowKey_${index}`}>
                            <Select
                                mode="multiple"
                                style={{
                                    width: '100%',
                                }}
                                defaultValue={()=>{
                                    console.log(typeof(item[el][0]))
                                    if(item[el].length > 0 && typeof(item[el][0])==='number'){
                                        return item[el]
                                    }else{
                                        return item[el].map(({id})=>(id))
                                    }
                                }}
                                placeholder="Выберите сайт(ы) для парсинга"
                                options={sites}
                                onChange={ChangeSitesHandler}
                            />
                        </td>
                        break;
                    case 'marker':
                        return <td key={`MyTableRowKey_${index}`}>
                            <Select
                                style={{
                                    width: '100%',
                                }}
                                disabled={item['status']==='ready' ? false : true }
                                defaultValue={item[el]}
                                options={markers}
                                onChange={ChangeMarkerHandler}
                            />
                        </td>
                        break;
                    case 'ip':
                        return <td key={`MyTableRowKey_${index}`}>
                           {item[el]}
                        </td>
                    case 'password':
                        return <td key={`MyTableRowKey_${index}`}>
                           {item[el]}
                        </td>
                    case 'type':
                        return <td key={`MyTableRowKey_${index}`}>
                           {item[el]}
                        </td>
                    case 'port':
                        return <td key={`MyTableRowKey_${index}`}>
                           {item[el]}
                        </td>
                    case 'login':
                        return <td key={`MyTableRowKey_${index}`}>
                           {item[el]}
                        </td>
                    default:
                        null
                        break;
                }
            }
            )  
        }
        
        {
            downloadResult
            ?
            <td><MyButton onClick={downloadResultHandler}>Скачать</MyButton></td>
            :
            null
        }
        {
            deleteRow
            ?
            <td>
                <MyButton onClick={deleteTaskHandler}>Удалить</MyButton>
            </td>
            :
            null
        }
        {
            runTask
            ?
            <td><MyButton onClick={runTaskHandler}>Запустить</MyButton></td>
            :
            null

        }
        
    </tr>
    )
}