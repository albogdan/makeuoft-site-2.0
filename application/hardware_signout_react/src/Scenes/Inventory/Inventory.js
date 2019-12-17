import React, { PureComponent } from 'react'
import styles from './inventory.module.scss';
import Component from '../../Components/Inventory/Component/Component';
import CheckoutHistory from './../../Components/Inventory/CheckoutHistory/CheckoutHistory';
import { ReactComponent as Search } from './../../Assets/Images/Icons/Search.svg'

export default class Inventory extends PureComponent {
  constructor(props) {
    super(props);
    this.state = { active: 0, popup: false, popupComponent: null,
                   components: null, showComponents: [], tagBtns: null}
    fetch('http://ieee.utoronto.ca/makeuoft/api/inventory')
      .then(response => response.json())
      .then(components => this.setState({ components }));
    fetch('http://ieee.utoronto.ca/makeuoft/api/taglist')
      .then(response => response.json())
      .then(tagBtns => this.setState({ tagBtns }));
  }

  sort(num) {
    let { components, tagBtns } = this.state;
    this.setState({ active: num, showComponents: [] });
    if (num === 9) {
      // this.setState({showComponents: this.state.components });
      //write A-Z function
    } else if (num === 10) {
      //write Z-A function
    } else {
      for (let i = 0; i < components.length; i++) {
        for (let j = 0; j < components[i].tags.length; j++) {
          if (tagBtns && components[i].tags[j] === tagBtns[num].name) {
            this.setState(state => {
              const showComponents = state.showComponents.concat(components[i]);
              return { showComponents };
            });
          }
        }
      }
    }
  }

  openPopup() {
    this.setState({popup: true});
  }

  closePopup() {
    this.setState({popup: false});
  }

  renderPopupComponent = (event) => {
    this.setState({popupComponent: event})
  }

  onkeyupCheck(evt, obj) {
    if (evt.keyCode === 13) {
        // document.getElementById("search-button").click();
        console.log("yoooo")
    } else if (!obj.value.trim()) {
        // _searchResult = [];
        // displayResult();
        this.searchInventory();
    }
  }

  searchInventory() {
    let { components } = this.state;
    JSON.Object(components);
    console.log(components)
  }

  render() {
    let { active, popup, popupComponent, components, showComponents, tagBtns } = this.state;
    const inventoryDataRecevied = (components===null);
    let tagButtons = [];

    if(tagBtns !== null){
      for (let i = 0; i < tagBtns.length; i++) {
        tagButtons.push(<button onClick={() => this.sort(i)} className={active === i ? styles['active'] : null}>{tagBtns[i].name}</button>);
      }
    }
    !inventoryDataRecevied && (active===0) && this.setState({showComponents: components});

    return (
      <div className={styles.inventory}>
        {popup &&
          <CheckoutHistory event={popupComponent} close={() => {this.closePopup()}}/>
        }

        <h1>Inventory</h1>
        <div className={styles.inventoryFilters}>
          {tagButtons}
          <div className={styles.inventoryFiltersSearch}>
            <Search />
            <input onKeyUp={(event) => this.onkeyupCheck(event, this)} placeholder="Search for a component..." />
          </div>

        </div>

        <div className={styles.inventoryList}>

          {inventoryDataRecevied ? (
            <p className={styles.inventoryListLoading}>Loading...</p>
          ) : (
            showComponents.map((item, i) => {
              return (
                <Component item={item.name} total={item.total} left={item.available} open={ () => {this.openPopup(); this.renderPopupComponent(item)}} />
              )
            })
          )}

        </div>
        {/* <p className={styles.inventoryToTop} onClick={() => {window.scrollTo({ top: 0, behavior: 'smooth'})}}>Back to top</p> */}
      </div>
    )
  }
}
