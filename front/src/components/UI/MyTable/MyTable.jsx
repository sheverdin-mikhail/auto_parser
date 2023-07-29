import React from 'react'
import './MyTable.module.css'
import MyTableRow from './MyTableRow'
import { Select } from 'antd';
import "antd/dist/antd.css";


export default function MyTable({tableData, downloadResult, deleteRow, saveSites, saveMarker, runTask, ...props}) {
      


    return (
    <div className='tableContainer'>
        <table className='myTable' cellSpacing='0' >
        {
            props.children
        }
        <tbody style={{'height': window.screen.height-window.screen.height*0.44}}>
            {tableData.map(item => {
               return <MyTableRow 
                item={item} 
                key={item.id} 
                deleteRow={deleteRow}
                runTask={runTask}
                downloadResult={downloadResult}
                saveSites={saveSites}
                saveMarker={saveMarker}
               />
            })}
        </tbody>
    </table>

    
    </div>
    )
}
