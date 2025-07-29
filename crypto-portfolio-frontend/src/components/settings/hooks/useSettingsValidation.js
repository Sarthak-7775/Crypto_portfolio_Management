export const useSettingsValidation = () => {
  const emailRegex = /^\S+@\S+\.\S+$/;
  const phoneRegex = /^\+?[0-9]{7,14}$/;

  return {
    validateEmail: (e) => emailRegex.test(e),
    validatePhone: (p) => phoneRegex.test(p),
  };
};
