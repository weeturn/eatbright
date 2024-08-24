import React, { useState } from 'react';
import InputForm from './components/InputForm';
import AnalysisResultTable from './components/AnalysisResultTable';
import RawReviewList from './components/RawReviewList';
import axios from 'axios';
import { Container, Grid, Box, Typography } from '@mui/material';

const App = () => {
    const [reviews, setReviews] = useState([]);
    const [topDishes, setTopDishes] = useState([]);
    const [worstDishes, setWorstDishes] = useState([]);
    const API_URL = process.env.REACT_APP_API_URL;

    const handleSearch = async (storeName, googleMapUrl) => {
        try {
            const scrapeResponse = await axios.post(`${API_URL}/scraper/`, {
                store_name: storeName,
                google_map_url: googleMapUrl,
            });
            console.log('Scrape Response:', scrapeResponse.data);
    
            setReviews(scrapeResponse.data.raw_reviews);
    
            if (scrapeResponse.data.top_dishes && scrapeResponse.data.worst_dishes) {
                setTopDishes(scrapeResponse.data.top_dishes);
                setWorstDishes(scrapeResponse.data.worst_dishes);
            } else {
                const analyzeResponse = await axios.post(`${API_URL}/gemini/`, {
                    store_id: scrapeResponse.data.store_id,
                });
    
                setTopDishes(analyzeResponse.data.top_dishes);
                setWorstDishes(analyzeResponse.data.worst_dishes);
            }
        } catch (error) {
            console.error('Error fetching reviews and analysis:', error);
        }
    };
    

    return (
        <Container>
            <Box my={4}>
                <InputForm onSearch={handleSearch} />
                <RawReviewList reviews={reviews} />
                <Box mt={4}>
                    <Typography variant="h5" gutterBottom>
                        Top 7 Dishes
                    </Typography>
                    <AnalysisResultTable dishes={topDishes} />
                </Box>
                <Box mt={4}>
                    <Typography variant="h5" gutterBottom>
                        Worst 5 Dishes
                    </Typography>
                    <AnalysisResultTable dishes={worstDishes} />
                </Box>
            </Box>
        </Container>
    );
};

export default App;
