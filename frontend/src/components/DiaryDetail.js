// src/components/DiaryDetail.js
import React from 'react';
import { useParams } from 'react-router-dom';

const DiaryDetail = () => {
    let { id } = useParams();

    // 这里只是一个简单的示例，实际应用中你需要根据ID从后端获取日记详情
    return (
        <div>
            <h2>Diary Detail - ID: {id}</h2>
            <p>This is a placeholder for a diary detail.</p>
        </div>
    );
};

export default DiaryDetail;
