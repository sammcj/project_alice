import React from 'react';
import {
    Typography,
    Card,
    CardContent,
    Box,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
} from '@mui/material';
import { Theme } from '@mui/material/styles';
import { makeStyles } from '@mui/styles';

const useStyles = makeStyles((theme: Theme) => ({
    card: {
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
    },
    titleContainer: {
        position: 'relative',
        backgroundColor: theme.palette.primary.main,
        color: theme.palette.primary.contrastText,
        padding: theme.spacing(2),
        borderRadius: theme.shape.borderRadius,
        marginBottom: theme.spacing(1),
    },
    title: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    elementType: {
        position: 'absolute',
        top: -10,
        left: 8,
        fontSize: '0.75rem',
        padding: '0 4px',
        backgroundColor: theme.palette.primary.main,
        borderRadius: 4,
    },
    subtitle: {
        marginBottom: theme.spacing(1),
    },
    id: {
        display: 'block',
        marginBottom: theme.spacing(2),
    },
    list: {
        padding: 0,
    },
    listItem: {
        width: '100%',
    }
}));

interface ListItemData {
    icon: React.ReactElement;
    primary_text: string;
    secondary_text: React.ReactNode;
}

interface CommonCardViewProps {
    title: string;
    elementType?: string;
    subtitle?: string;
    id?: string;
    listItems?: ListItemData[];
    children?: React.ReactNode;
}

const CommonCardView: React.FC<CommonCardViewProps> = ({ 
    title, 
    elementType, 
    subtitle, 
    id, 
    listItems, 
    children 
}) => {
    const classes = useStyles();

    return (
        <Card className={classes.card}>
            <CardContent>
                <Box className={classes.titleContainer}>
                    {elementType && (
                        <Typography variant="caption" className={classes.elementType}>
                            {elementType}
                        </Typography>
                    )}
                    <Typography variant="h5" className={classes.title}>
                        {title}
                    </Typography>
                </Box>
                {subtitle && (
                    <Typography variant="subtitle1" className={classes.subtitle}>{subtitle}</Typography>
                )}
                {id && (
                    <Typography variant="caption" className={classes.id}>
                        ID: {id}
                    </Typography>
                )}
                {listItems && listItems.length > 0 && (
                    <List className={classes.list}>
                        {listItems.map((item, index) => (
                            <ListItem key={index} className={classes.listItem}>
                                <ListItemIcon>{item.icon}</ListItemIcon>
                                <ListItemText
                                    primary={item.primary_text}
                                    secondary={item.secondary_text}
                                />
                            </ListItem>
                        ))}
                    </List>
                )}
                {children && <Box>{children}</Box>}
            </CardContent>
        </Card>
    );
};

export default CommonCardView;