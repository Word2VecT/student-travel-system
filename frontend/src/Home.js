// src/components/Home.js
import React from 'react';
import { Link } from 'react-router-dom';
import Button from '@mui/material/Button';

const Home = () => {
    return (
        <div>
            <h1>Welcome to the Student Travel System</h1>
            <Button variant="contained" component={Link} to="/map">Explore Map</Button>
            <Button variant="contained" component={Link} to="/diaries">View Diaries</Button>
        </div>
    );
};

export default Home;
