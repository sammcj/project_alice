import React from 'react';
import {
    Typography,
    Box,
    Stack
} from '@mui/material';
import { Language, DataObject, QueryBuilder } from '@mui/icons-material';
import { DataClusterComponentProps } from '../../../../types/DataClusterTypes';
import CommonCardView from '../../common/enhanced_component/CardView';
import ReferenceChip from '../ReferenceChip';
import ReferencesViewer from '../ReferencesViewer';

const DataClusterCardView: React.FC<DataClusterComponentProps> = ({
    item
}) => {
    if (!item) {
        return <Typography>No Data Cluster data available.</Typography>;
    }

    const renderEmbeddingChips = () => {
        if (!item.embeddings || item.embeddings.length === 0) {
            return <Typography color="text.secondary">No embedding chunks</Typography>;
        }

        return (
            <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
                {item.embeddings.map((chunk, index) => (
                    <ReferenceChip
                        key={chunk._id}
                        reference={chunk}
                        type="EmbeddingChunk"
                        view={true}
                        className="reference-chip"
                    />
                ))}
            </Stack>
        );
    };

    const listItems = [
        {
            icon: <DataObject />,
            primary_text: "Embedding Chunks",
            secondary_text: <Box sx={{ mt: 1 }}>{renderEmbeddingChips()}</Box>
        },
        {
            icon: <Language />,
            primary_text: "References",
            secondary_text: (
                <ReferencesViewer
                    references={item}
                />
            )
        },
        {
            icon: <QueryBuilder />,
            primary_text: "Created At",
            secondary_text: new Date(item.createdAt || '').toLocaleString()
        }
    ];

    return (
        <CommonCardView
            elementType='Data Cluster'
            title={'Data Cluster Details'}
            id={item._id}
            listItems={listItems}
            item={item}
            itemType='dataclusters'
        />
    );
};

export default DataClusterCardView;