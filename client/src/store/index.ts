import { configureStore, combineReducers } from '@reduxjs/toolkit';
import {
  persistStore,
  persistReducer,
  FLUSH,
  REHYDRATE,
  PAUSE,
  PERSIST,
  PURGE,
  REGISTER,
} from 'redux-persist';
import storage from 'redux-persist/lib/storage';

import authReducer from './slices/authSlice';
import userReducer from './slices/userSlice';
import themeReducer from './slices/themeSlice';
import pipelineReducer from './slices/pipelineSlice';
import satelliteReducer from './slices/satelliteSlice';
import analysisReducer from './slices/analysisSlice';
import alertReducer from './slices/alertSlice';
import uiReducer from './slices/uiSlice';

const persistConfig = {
  key: 'geospatial-app',
  version: 1,
  storage,
  whitelist: ['auth', 'theme', 'ui'],
};

const rootReducer = combineReducers({
  auth: authReducer,
  user: userReducer,
  theme: themeReducer,
  pipeline: pipelineReducer,
  satellite: satelliteReducer,
  analysis: analysisReducer,
  alerts: alertReducer,
  ui: uiReducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
  devTools: import.meta.env.DEV,
});

export const persistor = persistStore(store);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

