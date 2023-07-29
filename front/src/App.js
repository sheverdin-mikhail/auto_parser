import React, { useEffect, useState } from 'react';
import {
  BrowserRouter
} from "react-router-dom";
import AppRouter from './components/AppRouter';
import Navbar from './components/Navbar';
import { AuthContext } from './context';

import './styles/App.css'



export default function App() {
  const [isAuth, setIsAuth] = useState({auth: false})

  useEffect(()=>{
    if (localStorage.getItem('isAuth')){
      setIsAuth(JSON.parse(localStorage.getItem('isAuth')))
    }else{
      setIsAuth({auth: false})
    }
  }, [])

    return (
      <AuthContext.Provider value={{
          isAuth,
          setIsAuth
      }}>
        <BrowserRouter>
          <div className='container'>
            <Navbar/>
            <AppRouter/>
          </div>
        </BrowserRouter>
      </AuthContext.Provider>
    );
}
