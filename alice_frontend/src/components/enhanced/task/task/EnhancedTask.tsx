import React from 'react';
import { AliceChat } from '../../../../utils/ChatTypes';
import { AliceTask, TaskComponentProps } from '../../../../utils/TaskTypes';
import BaseDbElement, { BaseDbElementProps } from '../../common/enhanced_component/BaseDbElement';
import TaskFlexibleView from './TaskFlexibleView';
import TaskCardView from './TaskCardView';
import TaskListView from './TaskListView';
import TaskTableView from './TaskTableView';
import TaskExecuteView from './TaskExecuteView';
import TaskShortListView from './TaskShortListView';

type BaseTaskMode = BaseDbElementProps<AliceChat>['mode'];
type ExtendedTaskMode = 'list' | 'shortList' | 'card' | 'table' | 'execute';
type EnhancedTaskMode = BaseTaskMode | ExtendedTaskMode;

interface EnhancedTaskProps extends Omit<TaskComponentProps, 'items' | 'item' | 'onChange' | 'handleSave' | 'mode'> {
    mode: EnhancedTaskMode;
    itemId?: string;
    fetchAll: boolean;
    onSave?: (savedItem: AliceTask) => void;
    onExecute?: () => Promise<any>;
}

const EnhancedTask: React.FC<EnhancedTaskProps> = (props) => {
    const renderContent = (
        items: AliceTask[] | null,
        item: AliceTask | null,
        onChange: (newItem: Partial<AliceTask>) => void,
        mode: BaseTaskMode,
        handleSave: () => Promise<void>
    ) => {
        const commonProps: TaskComponentProps = {
            items,
            item,
            mode,
            onChange,
            handleSave,
            onInteraction: props.onInteraction,
            onView: props.onView,
            isInteractable: props.isInteractable,
            handleAgentClick: props.handleAgentClick,
            handleModelClick: props.handleModelClick,
            handleTaskClick: props.handleTaskClick,
            handlePromptClick: props.handlePromptClick,
            showHeaders: props.showHeaders,
        };
        switch (props.mode) {
            case 'create':
            case 'edit':
            case 'view':
                return <TaskFlexibleView {...commonProps} />;
            case 'shortList':
                return <TaskShortListView {...commonProps} />;
            case 'list':
                return <TaskListView {...commonProps} />;
            case 'table':
                return <TaskTableView {...commonProps} />;
            case 'card':
                return <TaskCardView {...commonProps} />;
            case 'execute':
                return <TaskExecuteView {...commonProps} onExecute={props.onExecute} />;
            default:
                return null;
        }
    };

    const baseDbMode: BaseDbElementProps<AliceTask>['mode'] =
        props.mode === 'create' ? 'create' :
            props.mode === 'edit' ? 'edit' : 'view';

    return (
        <BaseDbElement<AliceTask>
            collectionName="tasks"
            itemId={props.itemId}
            mode={baseDbMode}
            isInteractable={props.isInteractable}
            onInteraction={props.onInteraction}
            onSave={props.onSave}
            fetchAll={props.fetchAll}
            render={renderContent}
        />
    );
};

export default EnhancedTask;