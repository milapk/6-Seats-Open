import { createTheme } from "@mui/material/styles";

const theme = createTheme({
    palette: {
        mode: "dark",
        primary: {
            main: "#000000",
            contrastText: "#ffffff",
        },
        secondary: {
            main: "#ffffff",
            contrastText: "#000000",
        },
        text: {
            primary: "#FFFFFF",
            secondary: "#B3B3B3",
        },
    },
    typography: {
        button: {
          textTransform: 'none'
        }
      },
    components: {
        MuiTextField: {
            variants: [
                {
                    props: { size: "xsmall" },
                    style: {
                        "& .MuiInputBase-root": {
                            height: 38,
                            fontSize: "0.9rem",
                        },
                        "& .MuiInputLabel-root": {
                            fontSize: "0.9rem",
                            transform: "translate(3px, 8px) scale(1.2)",
                        },
                        "& .MuiInputLabel-shrink": {
                            transform: "translate(3px, 2px) scale(0.7)",
                        },
                        "& input": {
                            textAlign: 'left',
                            paddingLeft: "4px",
                            paddingBottom: '15px'
                        },
                    },
                },
            ],
        },
        MuiOutlinedInput: {
            styleOverrides: {
                root: {
                    "& fieldset": {
                        borderColor: "#444", 
                    },
                    "&:hover fieldset": {
                        borderColor: "#ffffff",
                    },
                    "&.Mui-focused fieldset": {
                        borderColor: "#ffffff",
                    },
                    input: {
                        color: "#fff",
                    },
                },
            },
        },
        MuiInputLabel: {
            styleOverrides: {
                root: {
                    color: "#B3B3B3",
                    "&.Mui-focused": {
                        color: "#fff",
                    },
                },
            },
        },
    },
});

export default theme;
