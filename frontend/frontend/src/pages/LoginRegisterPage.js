import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Dialog,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios'; 


const LoginRegisterPage = () => {
    const [mode, setMode] = useState('login'); // 'login' or 'register'
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [repeatPassword, setRepeatPassword] = useState('');
    const [error, setError] = useState('');
    const [openForgotDialog, setOpenForgotDialog] = useState(false);
    const navigate = useNavigate();


    const handlePasswordResetPending = async () => {
        try {
            const res = await axios.post('http://localhost:8000/api/password-reset-request/', {
                email,
            });

            console.log('Reset link sent to:', email);
            setOpenForgotDialog(false);
            navigate('/resend-email', { state: { email, version: 'resetPassword' } });
            
        } catch (error) {
            if (error.response) {
                const data = error.response.data;
                console.error('Error:', data);
                if (typeof data === 'object' && data !== null) {
                    const firstField = Object.keys(data)[0];
                    const firstMessage = data[firstField][0];
                    setError(firstMessage);
                } else {
                    setError('Something went wrong.');
                }
            } else {
                console.error('Network error:', error);
                setError('Connection error. Please try again later.');
            }
        }
    };

    const handleSubmit = async () => {
        setError('');

        if (!username || !password || (mode === 'register' && (!email || !repeatPassword))) {
            setError('Please fill in all fields.');
            return;
        }

        if (mode === 'register' && password !== repeatPassword) {
            setError('Passwords do not match.');
            return;
        }

        const endpoint = mode === 'login'
            ? 'http://localhost:8000/api/token/'
            : 'http://localhost:8000/api/register/';

        const payload = mode === 'login'
            ? { username, password }
            : { username, email, password };

        try {
            const res = await axios.post(endpoint, payload, { withCredentials: true });
            const data = res.data;

            console.log('Success:', data);

            if (mode === 'register') {
                navigate('/resend-email', { state: { email, version: 'verification' } });
            }

            if (mode === 'login') {
                const access = res.data.access;
                localStorage.setItem('access_token', access);
                axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
                navigate('/wardrobe');
            }
        } catch (error) {
            if (error.response && error.response.data) {
                const data = error.response.data;
                console.error('Error:', data);

                if (typeof data === 'object') {
                    const firstField = Object.keys(data)[0];
                    const firstMessage = Array.isArray(data[firstField])
                        ? data[firstField][0]
                        : 'Something went wrong.';
                    setError(firstMessage);
                } else {
                    setError('Something went wrong.');
                }
            } else {
                console.error('Connection error:', error);
                setError('Connection error. Please try again later.');
            }
        }
    };

    return (
        <Box
            sx={{
                height: '100vh',
                backgroundColor: '#e0f7fa',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: 600,
            }}
        >
            <Paper
                elevation={3}
                sx={{
                    height: '60vh',
                    p: 4,
                    width: 320,
                    borderRadius: 1,
                    textAlign: 'center',
                    display: 'flex',
                    flexDirection: 'column',
                    minHeight: 400,
                }}
            >
                {/* Pill button */}
                <Box
                    sx={{
                        position: 'relative',
                        display: 'flex',
                        backgroundColor: '#b2ebf2',
                        borderRadius: '100px',
                        p: '4px',
                        mb: 3,
                        mx: 4,
                        cursor: 'pointer',
                        userSelect: 'none',
                    }}
                >
                <Box
                    sx={{
                        position: 'absolute',
                        top: 4,
                        left: mode === 'login' ? '4px' : 'calc(50% - 4px)',
                        width: '50%',
                        height: 'calc(100% - 8px)',
                        backgroundColor: '#00bcd4',
                        borderRadius: '100px',
                        transition: 'left 0.3s ease',
                        zIndex: 1,
                    }}
                />
                {['login', 'register'].map((value) => (
                    <Box
                    key={value}
                    onClick={() => {setMode(value); setError('');}}
                    sx={{
                        zIndex: 2,
                        flex: 1,
                        textAlign: 'center',
                        paddingY: '6px',
                        fontWeight: 'normal',
                        color: mode === value ? 'white' : 'black',
                        transition: 'color 0.3s ease',
                    }}
                    >
                    {value === 'login' ? 'Log in' : 'Register'}
                    </Box>
                ))}
                </Box>

                {mode === 'login' ? (
                <>
                    <TextField
                        label="Username"
                        variant="standard"
                        fullWidth
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        sx={{ mb: 2 }}
                    />
                    <TextField
                        label="Password"
                        type="password"
                        variant="standard"
                        fullWidth
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        sx={{ mb: 5 }}
                    />
                </>
                ) : (
                <>
                    <TextField
                        label="Username"
                        variant="standard"
                        fullWidth
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        sx={{ mb: 2 }}
                    />
                    <TextField
                        label="E-mail"
                        variant="standard"
                        fullWidth
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        sx={{ mb: 2 }}
                    />
                    <TextField
                        label="Password"
                        type="password"
                        variant="standard"
                        fullWidth
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        sx={{ mb: 2 }}
                    />
                    <TextField
                        label="Repeat password"
                        type="password"
                        variant="standard"
                        fullWidth
                        value={repeatPassword}
                        onChange={(e) => setRepeatPassword(e.target.value)}
                        sx={{ mb: 6 }}
                    />
                </>
                )}

                {mode === 'login' && (
                    <Typography
                        variant="body2"
                        sx={{
                            mb: 6,
                            textDecoration: 'underline',
                            color: 'black',
                            cursor: 'pointer',
                            '&:hover': {color: '#0288d1',},
                        }}
                        onClick={() => setOpenForgotDialog(true)}
                    >
                        Forgot your password?
                    </Typography>
                )}

                {error && (
                    <Typography
                        color="error"
                        variant="body2"
                        sx={{ mb: 2, mt: -3 }}
                    >
                        {error}
                    </Typography>
                )}

                {/* Submit button */}
                <Button
                    variant="contained"
                    type="button"
                    onClick={handleSubmit}
                    sx={{
                        backgroundColor: '#00bcd4',
                        color: 'white',
                        borderRadius: 10,
                        width: '80%',
                        py: 1,
                        mt: 'auto',
                        alignSelf: 'center',
                        fontWeight: 'bold',
                        '&:hover': {
                        backgroundColor: '#00acc1',
                        },
                    }}
                >
                    {mode === 'login' ? 'Log in' : 'Register'}
                </Button>
            </Paper>
            <Dialog open={openForgotDialog} onClose={() => setOpenForgotDialog(false)}>
                <Box sx={{ p: 3, minWidth: 500 }}>
                    <Typography variant="h6" gutterBottom>
                         Reset your password
                    </Typography>

                    <TextField
                        label="E-mail"
                        type="email"
                        fullWidth
                        variant="standard"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        sx={{ mb: 1 }}
                    />

                    {error && (
                    <Typography variant="body2" color="error" sx={{ mb: 2 }}>
                        {error}
                    </Typography>
                    )}

                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                        <Button onClick={() => {
                            setOpenForgotDialog(false);
                            setError('');
                            }}
                        >
                            Cancel
                        </Button>
                        <Button
                            variant="contained"
                            onClick={handlePasswordResetPending}
                        >
                            Send
                        </Button>
                    </Box>
                </Box>
            </Dialog>
        </Box>
    )
};


export default LoginRegisterPage;
