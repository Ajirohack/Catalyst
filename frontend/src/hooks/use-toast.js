import { useState, useCallback } from 'react';

const useToast = () => {
    const [toasts, setToasts] = useState([]);

    const removeToast = useCallback((id) => {
        setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id));
    }, []);

    const addToast = useCallback((toast) => {
        const id = Math.random().toString(36).substr(2, 9);
        const newToast = {
            id,
            title: toast.title || '',
            description: toast.description || '',
            variant: toast.variant || 'default',
            duration: toast.duration || 5000,
            action: toast.action,
            ...toast
        };

        setToasts((prevToasts) => [...prevToasts, newToast]);

        if (newToast.duration > 0) {
            setTimeout(() => {
                removeToast(id);
            }, newToast.duration);
        }

        return id;
    }, [removeToast]);

    const toast = useCallback((options) => {
        if (typeof options === 'string') {
            return addToast({ description: options });
        }
        return addToast(options);
    }, [addToast]);

    toast.success = useCallback((options) => {
        return addToast({ ...options, variant: 'success' });
    }, [addToast]);

    toast.error = useCallback((options) => {
        return addToast({ ...options, variant: 'destructive' });
    }, [addToast]);

    toast.warning = useCallback((options) => {
        return addToast({ ...options, variant: 'warning' });
    }, [addToast]);

    return {
        toast,
        toasts,
        removeToast
    };
};

export { useToast };
