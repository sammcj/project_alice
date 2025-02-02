import React from 'react';
import { MessageComponentProps, MessageType } from '../../../../types/MessageTypes';
import EnhancedShortListView from '../../../common/enhanced_component/ShortListView';

const MessageShortListView: React.FC<MessageComponentProps> = ({
    items,
    item,
    onInteraction,
    onView,
}) => {
    const getPrimaryText = (message: MessageType) => `${message.role}: ${message.content.substring(0, 300)}${message.content.length > 300 ? '...' : ''}`;
    const getSecondaryText = (message: MessageType) => `Generated by: ${message.generated_by} | ${new Date(message.createdAt || '').toLocaleString()}`;

    return (
        <EnhancedShortListView<MessageType>
            items={items as MessageType[]}
            item={item as MessageType}
            getPrimaryText={getPrimaryText}
            getSecondaryText={getSecondaryText}
            onView={onView}
            onInteraction={onInteraction}
        />
    );
};

export default MessageShortListView;