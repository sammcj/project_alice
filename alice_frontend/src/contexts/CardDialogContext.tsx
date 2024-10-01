import React, { createContext, useContext, useState, useCallback } from 'react';
import { CollectionElementString, CollectionElement } from '../types/CollectionTypes';

interface DialogContextType {
  selectItem: (itemType: CollectionElementString, itemId?: string, item?: CollectionElement) => void;
  selectedItem: CollectionElement | null;
  selectedItemType: CollectionElementString | null;
  handleClose: () => void;
}

const CardDialogContext = createContext<DialogContextType | undefined>(undefined);

export const DialogProvider: React.FC<React.PropsWithChildren<{}>> = ({ children }) => {
  const [selectedItem, setSelectedItem] = useState<CollectionElement | null>(null);
  const [selectedItemType, setSelectedItemType] = useState<CollectionElementString | null>(null);

  const selectItem = useCallback((itemType: CollectionElementString, itemId?: string, item?: CollectionElement) => {
    console.log('Selecting item:', itemType, itemId, item);
    setSelectedItemType(itemType);
    if (item) {
      setSelectedItem(item);
    } else if (itemId) {
      setSelectedItem({ _id: itemId } as CollectionElement);
    } else {
      setSelectedItem(null);
    }
  }, []);

  const handleClose = useCallback(() => {
    setSelectedItem(null);
    setSelectedItemType(null);
  }, []);

  return (
    <CardDialogContext.Provider value={{ selectItem, selectedItem, selectedItemType, handleClose }}>
      {children}
    </CardDialogContext.Provider>
  );
};

export const useCardDialog = () => {
  const context = useContext(CardDialogContext);
  if (context === undefined) {
    throw new Error('useDialog must be used within a DialogProvider');
  }
  return context;
};