import React, { useCallback, useState } from 'react';
import { Box, Typography, Button, Card, CardContent, CircularProgress } from '@mui/material';
import { Warning } from '@mui/icons-material';
import useStyles from '../../../styles/UserSettingsStyles';
import { useDialog } from '../../../contexts/DialogContext';
import { useApi } from '../../../contexts/ApiContext';
import { useNotification } from '../../../contexts/NotificationContext';
import Logger from '../../../utils/Logger';

const DangerZone: React.FC = () => {
    const classes = useStyles();
    const { openDialog } = useDialog();
    const { purgeAndReinitializeDatabase } = useApi();
    const { addNotification } = useNotification();
    const [isLoading, setIsLoading] = useState(false);

    const handlePurgeAndReinitialize = useCallback(() => {
        Logger.debug('handlePurgeAndReinitialize called');
        openDialog({
            title: 'Confirm Database Purge and Reinitialization',
            content: 'Are you sure you want to purge and reinitialize your database? This action cannot be undone and will delete all your current data.',
            buttons: [
                {
                    text: 'Cancel',
                    action: () => {
                        addNotification('Database reinitialization cancelled', 'info');
                    },
                    color: 'primary',
                },
                {
                    text: 'Confirm Purge and Reinitialize',
                    action: async () => {
                        Logger.debug('Dialog confirmed');
                        setIsLoading(true);
                        try {
                            Logger.debug('Purging db');
                            await purgeAndReinitializeDatabase();
                            Logger.debug('Database successfully purged and reinitialized');
                            addNotification('Database successfully purged and reinitialized', 'success');
                            window.location.reload();
                        } catch (error) {
                            Logger.error('Failed to purge and reinitialize database:', error);
                            addNotification('Failed to purge and reinitialize database. Please try again.', 'error');
                        } finally {
                            setIsLoading(false);
                        }
                    },
                    color: 'error',
                    variant: 'contained',
                },
            ],
        });
    }, [openDialog, purgeAndReinitializeDatabase, addNotification]);

    return (
        <Card className={classes.card}>
            <CardContent>
                <Box className={classes.dangerZone}>
                    <Box className={classes.userInfoHeader}>
                        <Warning color="error" />
                        <Typography variant="h5">Danger Zone</Typography>
                    </Box>
                    <Typography variant="body1" color="error" paragraph>
                        The following action will delete all your data and reinitialize your database. This cannot be undone.
                    </Typography>
                    <Button
                        variant="contained"
                        onClick={() => {
                            if (!isLoading) {
                                Logger.debug('Purge button clicked');
                                handlePurgeAndReinitialize();
                            }
                        }}
                        className={classes.dangerButton}
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <CircularProgress size={24} color="inherit" />
                        ) : (
                            'Purge and Reinitialize Database'
                        )}
                    </Button>
                </Box>
            </CardContent>
        </Card>
    );
};

export default DangerZone;