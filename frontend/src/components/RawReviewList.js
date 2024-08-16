import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

const RawReviewList = ({ reviews = [] }) => {
    return (
        <TableContainer component={Paper}>
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>評論</TableCell>
                        <TableCell>相對日期</TableCell>
                        <TableCell>評分</TableCell>
                        <TableCell>用戶名稱</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {reviews.map((review, index) => (
                        <TableRow key={index}>
                            <TableCell>{review.text}</TableCell>
                            <TableCell>{review.relative_date}</TableCell>
                            <TableCell>{review.rating}</TableCell>
                            <TableCell>{review.user_name}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
};

export default RawReviewList;
