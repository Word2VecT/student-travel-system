// src/components/DiariesList.js
import React from 'react';
import { Link } from 'react-router-dom';

const DiariesList = () => {
    // 假设数据
    const diaries = [{ id: 1, title: 'My Trip to Paris' }, { id: 2, title: 'Weekend in New York' }];

    return (
        <div>
            <h2>Diaries List</h2>
            <ul>
                {diaries.map(diary => (
                    <li key={diary.id}>
                        <Link to={`/diaries/${diary.id}`}>{diary.title}</Link>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default DiariesList;
