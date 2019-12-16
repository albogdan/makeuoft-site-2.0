export const colourStyles = {
    control: (styles, state) => ({ 
        ...styles, 
        backgroundColor: 'white', 
        borderColor: state.isFocused ? '#3386BA' :'#ccc',
        boxShadow: state.isFocused && `0 0 0 1px #3386BA`
     }),
    option: (provided, state) => ({
        ...provided,
        fontSize: 14,
    }),
    placeholder: () => ({ fontSize: 14 }),
    singleValue: () => ({ fontSize: 14 }),
    groupHeading: () => ({ fontSize: 12, padding: 12, paddingTop: 0, color: '#3386BA', fontWeight: 'bold' }),
};

export const groupStyles = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  };
  
export const groupBadgeStyles = {
    backgroundColor: '#EBECF0',
    borderRadius: '2em',
    color: '#172B4D',
    display: 'inline-block',
    fontSize: 12,
    fontWeight: 'normal',
    lineHeight: '1',
    minWidth: 1,
    padding: '0.17em 0.5em',
    textAlign: 'center',
  };