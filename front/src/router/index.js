import Control from '../pages/Control'
import Login from '../pages/Login'
import Parser from '../pages/Parser'
import Root from '../pages/Root'
import Api from '../pages/Api'



export const privateRoutes = [
    // {path: '/main', page: Main, exact: true},
    {path: '/parser', page: Parser, exact: true},
    {path: '/api-panel', page: Api, exact: true},
    {path: '/control', page: Control, exact: true},
    {path: '/root', page: Root, exact: true},
]


export const publicRoutes = [
    {path: '/login', page: Login, exact: true},
]