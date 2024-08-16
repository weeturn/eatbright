import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

const AnalysisResultTable = ({ dishes = [] }) => {
    return (
        <TableContainer component={Paper}>
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>名稱</TableCell>
                        <TableCell>平均分數</TableCell>
                        <TableCell>出現次數</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {dishes.map((dish, index) => (
                        <TableRow key={index}>
                            <TableCell>{dish.dish_name}</TableCell>
                            <TableCell>{dish.score}</TableCell>
                            <TableCell>{dish.times}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
};

export default AnalysisResultTable;
