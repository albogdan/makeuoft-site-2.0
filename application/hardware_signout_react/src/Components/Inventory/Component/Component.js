import React, { PureComponent } from 'react'
import styles from './component.module.scss';


export default class Component extends PureComponent {

    render() {
        let { item, total, left, open, isCheckout} = this.props;

        return (
            <div className={`${styles.component} ${isCheckout ? styles['checkout'] : null}`} onClick={open}>
                <img src={require('./../../../Assets/Images/Components/' + item + '.jpg')} alt={item} />
                <div className={styles.componentDiv}>
                        <p className={styles.componentDivName}>{item}</p>
                    {(left > 0) ?
                        <p className={styles.componentDivStock}>{left} of {total} in stock</p>
                        :
                        <p className={styles.componentDivStock}>OUT OF STOCK</p>
                    }
                </div>
            </div>
        )
    }
}
