import { createContext, useContext, useReducer } from "react";

const initialState = {
  user: {
    name: "",
    email: "",
    phone: "",
    avatar: "",
    kycDocs: [],
  },
  bankAccounts: [],
  linkedAccounts: [],
  notifications: {
    email: true,
    sms: false,
    push: true,
  },
  privacy: {
    profileVisible: true,
    twoFactor: false,
  },
  theme: "system", // 'light' | 'dark' | 'system'
};

function reducer(state, action) {
  switch (action.type) {
    case "SET_USER":
      return { ...state, user: { ...state.user, ...action.payload } };
    case "SET_BANK_ACCOUNTS":
      return { ...state, bankAccounts: action.payload };
    case "SET_LINKED_ACCOUNTS":
      return { ...state, linkedAccounts: action.payload };
    case "SET_NOTIFICATIONS":
      return { ...state, notifications: { ...state.notifications, ...action.payload } };
    case "SET_PRIVACY":
      return { ...state, privacy: { ...state.privacy, ...action.payload } };
    case "SET_THEME":
      return { ...state, theme: action.payload };
    default:
      return state;
  }
}

const SettingsContext = createContext();

export function SettingsProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  return (
    <SettingsContext.Provider value={{ state, dispatch }}>
      {children}
    </SettingsContext.Provider>
  );
}

export const useSettings = () => useContext(SettingsContext);
