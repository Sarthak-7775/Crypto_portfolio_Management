import { useSettings } from "../context/SettingsContext";

export default function useUserSettings() {
  const { state, dispatch } = useSettings();
  return {
    user: state.user,
    updateUser: (payload) => dispatch({ type: "SET_USER", payload }),
  };
}
