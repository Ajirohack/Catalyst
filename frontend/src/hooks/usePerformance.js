import { useState, useCallback, useRef, useEffect } from 'react';

/**
 * Hook to detect when an element is visible in the viewport
 * Used for lazy loading components or implementing infinite scroll
 * 
 * @param {Object} options - Intersection observer options
 * @param {string} options.root - The element that is used as the viewport
 * @param {string} options.rootMargin - Margin around the root
 * @param {number} options.threshold - A number between 0 and 1 indicating the percentage that should be visible
 * @returns {[React.RefObject, boolean]} A tuple with a ref to attach and a boolean indicating if the element is visible
 */
export const useInView = (options = {}) => {
    const [isInView, setIsInView] = useState(false);
    const ref = useRef(null);

    const callback = useCallback(
        (entries) => {
            const [entry] = entries;
            setIsInView(entry.isIntersecting);
        },
        []
    );

    useEffect(() => {
        const observer = new IntersectionObserver(callback, options);
        const currentRef = ref.current;

        if (currentRef) {
            observer.observe(currentRef);
        }

        return () => {
            if (currentRef) {
                observer.unobserve(currentRef);
            }
        };
    }, [ref, options, callback]);

    return [ref, isInView];
};

/**
 * Hook to defer loading of expensive components until they are needed
 * 
 * @param {boolean} active - Whether the component should be considered for deferred loading
 * @param {number} delay - Optional delay in ms before loading the component
 * @returns {boolean} Whether the component should be rendered
 */
export const useDeferredLoading = (active = true, delay = 0) => {
    const [shouldLoad, setShouldLoad] = useState(!active);

    useEffect(() => {
        if (!active || shouldLoad) return;

        const timer = setTimeout(() => {
            setShouldLoad(true);
        }, delay);

        return () => clearTimeout(timer);
    }, [active, delay, shouldLoad]);

    return shouldLoad;
};

/**
 * Hook to implement virtualized lists for better performance with large datasets
 * 
 * @param {Object} options - Options for the virtualized list
 * @param {number} options.itemCount - Total number of items
 * @param {number} options.itemHeight - Height of each item in pixels
 * @param {number} options.windowHeight - Visible window height in pixels
 * @param {number} options.overscan - Number of items to render beyond the visible window
 * @returns {Object} The virtualized list properties and methods
 */
export const useVirtualList = ({
    itemCount,
    itemHeight,
    windowHeight,
    overscan = 3,
}) => {
    const [scrollTop, setScrollTop] = useState(0);

    const handleScroll = useCallback((event) => {
        setScrollTop(event.target.scrollTop);
    }, []);

    const visibleStartIndex = Math.floor(scrollTop / itemHeight);
    const visibleEndIndex = Math.min(
        itemCount - 1,
        Math.floor((scrollTop + windowHeight) / itemHeight)
    );

    const startIndex = Math.max(0, visibleStartIndex - overscan);
    const endIndex = Math.min(itemCount - 1, visibleEndIndex + overscan);

    const visibleItems = Array.from(
        { length: endIndex - startIndex + 1 },
        (_, index) => startIndex + index
    );

    const totalHeight = itemCount * itemHeight;
    const offsetY = startIndex * itemHeight;

    return {
        virtualItems: visibleItems,
        startIndex,
        endIndex,
        handleScroll,
        totalHeight,
        offsetY,
    };
};

/**
 * Hook to manage resource loading states for optimized UI rendering
 * 
 * @returns {Object} Functions to manage loading states
 */
export const useResourceLoader = () => {
    const [resources, setResources] = useState({
        // Track status of each resource
        // e.g. { users: { loading: false, loaded: false, error: null } }
    });

    const registerResource = useCallback((resourceName) => {
        setResources((prev) => ({
            ...prev,
            [resourceName]: { loading: false, loaded: false, error: null },
        }));
    }, []);

    const startLoading = useCallback((resourceName) => {
        setResources((prev) => ({
            ...prev,
            [resourceName]: { loading: true, loaded: false, error: null },
        }));
    }, []);

    const finishLoading = useCallback((resourceName, error = null) => {
        setResources((prev) => ({
            ...prev,
            [resourceName]: { loading: false, loaded: !error, error },
        }));
    }, []);

    const getResourceStatus = useCallback(
        (resourceName) => {
            return resources[resourceName] || { loading: false, loaded: false, error: null };
        },
        [resources]
    );

    const shouldLoadResource = useCallback(
        (resourceName) => {
            const status = getResourceStatus(resourceName);
            return !status.loading && !status.loaded;
        },
        [getResourceStatus]
    );

    return {
        registerResource,
        startLoading,
        finishLoading,
        getResourceStatus,
        shouldLoadResource,
        resources,
    };
};

export default {
    useInView,
    useDeferredLoading,
    useVirtualList,
    useResourceLoader,
};
