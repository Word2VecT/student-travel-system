// App.js
import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Home from './components/Home';
import MapView from './components/MapView';
import DiariesList from './components/DiariesList';
import DiaryDetail from './components/DiaryDetail';

function App() {
  return (
    <Router>
      <div>
        <Switch>
          <Route path="/" exact component={Home} />
          <Route path="/map" component={MapView} />
          <Route path="/diaries" exact component={DiariesList} />
          <Route path="/diaries/:id" component={DiaryDetail} />
        </Switch>
      </div>
    </Router>
  );
}

export default App;

