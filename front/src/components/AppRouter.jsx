import { Switch, Route, Redirect } from 'react-router-dom'
import React, { useContext } from 'react'
import { privateRoutes, publicRoutes } from '../router';
import { AuthContext } from '../context';

const  AppRouter = () =>  {

    const {isAuth} = useContext(AuthContext)
  return (
    isAuth.auth === true
    ?
    <Switch>
        {
            privateRoutes.map(route => {
                return <Route path={route.path} component={route.page} exact={route.exact} key={route.path} />
            })
        }
    <Redirect to='/control' />
    </Switch>
    :
    <Switch>
    {
        publicRoutes.map(route => {
            return <Route path={route.path} component={route.page} exact={route.exact} key={route.path} />
        })
    }
    <Redirect to='/login' />
    </Switch>
  )
}

export default AppRouter;