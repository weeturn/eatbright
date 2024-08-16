import React, { useState } from 'react';
import { TextField, Button, Grid } from '@mui/material';

const InputForm = ({ onSearch }) => {
    const [storeName, setStoreName] = useState('');
    const [googleMapUrl, setGoogleMapUrl] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        onSearch(storeName, googleMapUrl);
    };

    return (
        <form onSubmit={handleSubmit}>
            <Grid container spacing={2}>
                <Grid item xs={12} sm={5}>
                    <TextField
                        fullWidth
                        label="輸入店名"
                        variant="outlined"
                        value={storeName}
                        onChange={(e) => setStoreName(e.target.value)}
                        required
                    />
                </Grid>
                <Grid item xs={12} sm={5}>
                    <TextField
                        fullWidth
                        label="輸入Google Maps URL"
                        variant="outlined"
                        value={googleMapUrl}
                        onChange={(e) => setGoogleMapUrl(e.target.value)}
                        required
                    />
                </Grid>
                <Grid item xs={12} sm={2}>
                    <Button type="submit" variant="contained" color="primary" fullWidth>
                        搜尋
                    </Button>
                </Grid>
            </Grid>
        </form>
    );
};

export default InputForm;
