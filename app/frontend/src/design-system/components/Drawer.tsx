import React from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import { Button } from "./Button";
import "../components.css";

export interface DrawerProps {
  open?: boolean;
  isOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
  onClose?: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
}

export const Drawer: React.FC<DrawerProps> = ({
  open,
  isOpen,
  onOpenChange,
  onClose,
  title,
  description,
  children
}) => {
  const isDrawerOpen = isOpen !== undefined ? isOpen : (open ?? false);
  const handleOpenChange = (nextOpen: boolean) => {
    if (onOpenChange) onOpenChange(nextOpen);
    if (!nextOpen && onClose) onClose();
  };

  return (
    <Dialog.Root open={isDrawerOpen} onOpenChange={handleOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="hcm-dialog-overlay" />
        <Dialog.Content className="hcm-drawer-content" aria-describedby={description ? "drawer-desc" : undefined}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--color-divider)", paddingBottom: "var(--space-3)" }}>
            <div>
              <Dialog.Title style={{ fontSize: "var(--font-size-title-page)", fontWeight: "var(--font-weight-semibold)", color: "var(--color-text-primary)" }}>
                {title}
              </Dialog.Title>
              {description && (
                <Dialog.Description id="drawer-desc" style={{ fontSize: "var(--font-size-small)", color: "var(--color-text-secondary)", marginTop: "var(--space-1)" }}>
                  {description}
                </Dialog.Description>
              )}
            </div>
            <Dialog.Close asChild>
              <Button variant="ghost" size="sm" aria-label="Close drawer" onClick={onClose}>
                <X size={18} aria-hidden="true" />
              </Button>
            </Dialog.Close>
          </div>
          <div style={{ flex: 1, overflowY: "auto" }}>
            {children}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
};
