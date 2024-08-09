import React, { createContext, useContext, useState, useCallback } from 'react';
import { CollectionElementString } from '../types/CollectionTypes';

interface DialogContextType {
  selectItem: (itemType: CollectionElementString, itemId: string) => void;
  selectedItem: { _id: string } | null;
  selectedItemType: CollectionElementString | null;
  handleClose: () => void;
}

const DialogContext = createContext<DialogContextType | undefined>(undefined);

export const DialogProvider: React.FC<React.PropsWithChildren<{}>> = ({ children }) => {
  const [selectedItem, setSelectedItem] = useState<{ _id: string } | null>(null);
  const [selectedItemType, setSelectedItemType] = useState<CollectionElementString | null>(null);

  const selectItem = useCallback((itemType: CollectionElementString, itemId: string) => {
    setSelectedItemType(itemType);
    setSelectedItem({ _id: itemId });
  }, []);

  const handleClose = useCallback(() => {
    setSelectedItem(null);
    setSelectedItemType(null);
  }, []);

  return (
    <DialogContext.Provider value={{ selectItem, selectedItem, selectedItemType, handleClose }}>
      {children}
    </DialogContext.Provider>
  );
};

export const useDialog = () => {
  const context = useContext(DialogContext);
  if (context === undefined) {
    throw new Error('useDialog must be used within a DialogProvider');
  }
  return context;
};